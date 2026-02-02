#!/usr/bin/env python3
import os
import math
import time
import argparse

import rospy
from sensor_msgs.msg import Image
from gazebo_msgs.srv import GetModelState, SetModelState
from gazebo_msgs.msg import ModelState
from cv_bridge import CvBridge


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def quat_from_yaw(yaw: float):
    # yaw-only quaternion (x=y=0)
    # z = sin(yaw/2), w = cos(yaw/2)
    return (0.0, 0.0, math.sin(yaw * 0.5), math.cos(yaw * 0.5))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_topic", default="/camera/image_raw",
                        help="ROS image topic (use `rostopic list | grep image` to confirm)")
    parser.add_argument("--car_model", default="automobile",
                        help="Gazebo model name of the car (default from rcCar_assembly)")
    parser.add_argument("--output_dir", default="dataset",
                        help="Where to save images")
    parser.add_argument("--radius", type=float, default=1.2,
                        help="Distance from sign (meters)")
    parser.add_argument("--heights", type=str, default="0.15,0.25",
                        help="Comma heights relative to sign z (meters)")
    parser.add_argument("--angles_deg", type=str, default="-60,-40,-20,0,20,40,60",
                        help="Comma angles around the sign (degrees)")
    parser.add_argument("--shots_per_pose", type=int, default=1,
                        help="How many images to take at each pose")
    parser.add_argument("--sleep", type=float, default=0.25,
                        help="Small wait after moving car, seconds")
    args = parser.parse_args(rospy.myargv()[1:])

    rospy.init_node("synthetic_capture", anonymous=True)
    bridge = CvBridge()

    # Parse parameters
    heights = [float(x.strip()) for x in args.heights.split(",") if x.strip()]
    angles = [math.radians(float(x.strip())) for x in args.angles_deg.split(",") if x.strip()]

    # Service clients
    rospy.wait_for_service("/gazebo/get_model_state")
    rospy.wait_for_service("/gazebo/set_model_state")
    get_state = rospy.ServiceProxy("/gazebo/get_model_state", GetModelState)
    set_state = rospy.ServiceProxy("/gazebo/set_model_state", SetModelState)

    # Define which signs to capture
    # Based on your launch files:
    # - STOP signs: STOP_A, STOP_C, STOP_E, STOP_G, STOP_W, ...
    # - Parking signs: PRK_P1..PRK_P4
    stop_signs = ["STOP_A", "STOP_C", "STOP_E", "STOP_G", "STOP_W", "STOP_Y", "STOP_Z"]
    parking_signs = ["PRK_P1", "PRK_P2", "PRK_P3", "PRK_P4"]

    targets = [
        ("STOP", stop_signs),
        ("PARKING", parking_signs),
    ]

    ensure_dir(args.output_dir)

    # Quick sanity check: can we read an image topic?
    rospy.loginfo(f"[capture] Waiting for one image on {args.image_topic} ...")
    try:
        rospy.wait_for_message(args.image_topic, Image, timeout=5.0)
    except Exception:
        rospy.logerr(
            f"[capture] Can't read image from {args.image_topic}\n"
            f"Run: rostopic list | grep image\n"
            f"Then re-run with: --image_topic <correct_topic>"
        )
        return

    rospy.loginfo("[capture] Image topic OK ✅ Starting capture...")

    for label, sign_list in targets:
        out_label_dir = os.path.join(args.output_dir, label)
        ensure_dir(out_label_dir)

        for sign_name in sign_list:
            # Get sign pose
            try:
                sign_state = get_state(sign_name, "world")
            except Exception as e:
                rospy.logwarn(f"[capture] Could not find sign model '{sign_name}' (skipping). Error: {e}")
                continue

            sx = sign_state.pose.position.x
            sy = sign_state.pose.position.y
            sz = sign_state.pose.position.z

            idx = 0
            for h in heights:
                for ang in angles:
                    # Position the car around the sign on a circle
                    # car position = sign position + radius in direction ang
                    cx = sx + args.radius * math.cos(ang)
                    cy = sy + args.radius * math.sin(ang)
                    cz = sz + h

                    # Make the car face the sign:
                    # yaw should point from car -> sign
                    yaw = math.atan2((sy - cy), (sx - cx))
                    qx, qy, qz, qw = quat_from_yaw(yaw)

                    # Set car pose
                    ms = ModelState()
                    ms.model_name = args.car_model
                    ms.reference_frame = "world"
                    ms.pose.position.x = cx
                    ms.pose.position.y = cy
                    ms.pose.position.z = cz
                    ms.pose.orientation.x = qx
                    ms.pose.orientation.y = qy
                    ms.pose.orientation.z = qz
                    ms.pose.orientation.w = qw

                    try:
                        set_state(ms)
                    except Exception as e:
                        rospy.logwarn(f"[capture] Failed to move car '{args.car_model}'. Error: {e}")
                        continue

                    time.sleep(args.sleep)

                    # Take screenshots
                    for s in range(args.shots_per_pose):
                        try:
                            msg = rospy.wait_for_message(args.image_topic, Image, timeout=2.0)
                            cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
                        except Exception as e:
                            rospy.logwarn(f"[capture] Image capture failed at {sign_name}. Error: {e}")
                            continue

                        idx += 1
                        filename = f"{sign_name}_{idx:04d}.png"
                        filepath = os.path.join(out_label_dir, filename)

                        # Save
                        try:
                            import cv2
                            cv2.imwrite(filepath, cv_img)
                        except Exception as e:
                            rospy.logerr(f"[capture] Failed to save image: {filepath}. Error: {e}")
                            continue

                        rospy.loginfo(f"[capture] Saved {filepath}")

    rospy.loginfo("[capture] DONE ✅ Dataset created.")


if __name__ == "__main__":
    main()
