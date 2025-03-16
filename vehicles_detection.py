import sys

import cv2
import numpy as np
from ultralytics import YOLO
import argparse

def analyzing_speed_vehicles(fps, cap, model, previous_positions, max_speed, frame_id, fastest_vehicle_id):
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        frame_id += 1
        results = model(frame)
        current_positions = {}  # Creating position in currently frame

        for result in results:
            for i, box in enumerate(result.boxes):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()
                cls = int(box.cls[0])
                label = f"{model.names[cls]}: {conf:.2f}"
                detection_vehicles = ["car", "bus", "truck"]
                for vehicle in detection_vehicles:
                    if vehicle in label:
                        x_center = (x1 + x2) // 2  # Centar of x
                        y_center = (y1 + y2) // 2  # Centar of y
                        current_positions[i] = (x_center, y_center)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # Calculating speed and include previous car
                        if i in previous_positions:
                            x_prev, y_prev = previous_positions[i]
                            distance = np.sqrt((x_center - x_prev) ** 2 + (y_center - y_prev) ** 2)  # Euclidian
                            speed = distance * fps  # Task is calculating speed px/sec
                            max_speed = max(max_speed, speed)# Choose the max speed
                            fastest_vehicle_id = model.names[i]
                            cv2.putText(frame, f"{speed:.2f} px/s", (x_center, y_center - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        previous_positions = current_positions  # Updating position

        cv2.imshow("Vehicle Speed Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    return f"Max speed is : {max_speed:.2f} px/s | Vehicle ID: {fastest_vehicle_id}"


def argparser():
    parser = argparse.ArgumentParser(description="This program detection vehicles speed.")
    parser.add_argument("--video", type=str, help="Path to .mp4 video")
    parser.add_argument("--model", type=str,default="yolov8s.pt", help="Models for detection use which one you want, default values is yolov8s.pt")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = argparser()
    if args.video:
        cap = cv2.VideoCapture(args.video)
        fps = cap.get(cv2.CAP_PROP_FPS)
    else:
        sys.exit("Argument --video is required. Put path to your .mp4 video.")

    model = YOLO(args.model) #Model arument has default vaules

    print(analyzing_speed_vehicles(fps = fps, cap = cap, model = model, previous_positions = {}, max_speed = 0, frame_id = 0, fastest_vehicle_id=None))








