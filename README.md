# ArUco Marker Tracking System

A real-time autonomous spatial tracking and guidance system built with Python and OpenCV.
Detects ArUco markers using a standard laptop webcam and displays live movement commands.

---

## What It Does

- Detects ArUco markers (DICT_5X5_50) in real-time using webcam
- Draws a fixed crosshair at the exact center of the video frame
- Draws a dynamic error vector (arrow) from frame center to the detected marker
- Displays movement commands that update live:
  - MOVE LEFT
  - MOVE RIGHT
  - MOVE UP
  - MOVE DOWN
- Shows **LOCK ENGAGED** when marker is centered within ±10 pixels
- Handles edge cases gracefully (does not crash when marker leaves frame)

---

## Libraries Used

| Library | Version | Purpose |
|---------|---------|---------|
| opencv-python | 4.13.0 | Webcam capture and drawing |
| opencv-contrib-python | 4.13.0 | ArUco marker detection |
| numpy | 2.4.4 | Coordinate calculations |

---

## Installation

Make sure Python is installed, then run:

```bash
pip install opencv-python
pip install opencv-contrib-python
pip install numpy
```

---

## How to Run

```bash
python main.py
```

---

## How to Generate ArUco Marker

1. Open [chev.me/aruco/](https://chev.me/aruco/) on your phone
2. Set Dictionary to **5x5 (50 markers)**
3. Set Marker ID to **0**
4. Set phone brightness to maximum
5. Hold phone screen in front of your webcam

---

## How It Works

1. Webcam captures live video at 640x480 resolution
2. Each frame is converted to grayscale
3. OpenCV ArUco detector scans for markers
4. If marker found — centroid (center point) is calculated
5. Error offset is computed: `dx = marker_x - 320`, `dy = marker_y - 240`
6. Movement command is determined based on dx and dy values
7. If both dx and dy are within ±10 pixels — LOCK ENGAGED is displayed

---

## Project Structure

```
aruco-tracking-system/
│
└── main.py        # Main tracking script
└── README.md      # This file
```

---

## Controls

| Key | Action |
|-----|--------|
| Q | Quit the program |

---

## Target Platform

- OS: Windows / Linux / Mac
- Camera: Standard laptop webcam (640x480)
- Target: ArUco marker on phone screen or printed paper

