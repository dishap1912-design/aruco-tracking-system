"""
ArUco Marker Tracking System
=============================
Tracks an ArUco marker using webcam and displays:
- Fixed crosshair at frame center
- Dynamic error vector (arrow) from center to marker
- Movement commands (MOVE LEFT/RIGHT/UP/DOWN, APPROACH)
- LOCK ENGAGED when marker is centered within +-10 pixels

Requirements: opencv-python, opencv-contrib-python, numpy
Run: python main.py
"""

import cv2
import numpy as np

# ─────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CENTER_X = FRAME_WIDTH // 2    # 320
CENTER_Y = FRAME_HEIGHT // 2   # 240
LOCK_THRESHOLD = 10            # pixels - within this = LOCK ENGAGED

# ArUco dictionary (DICT_5X5_50 as required by task)
ARUCO_DICT = cv2.aruco.DICT_5X5_50

# Colors (BGR format for OpenCV)
COLOR_GREEN  = (0, 255, 0)
COLOR_RED    = (0, 0, 255)
COLOR_BLUE   = (255, 100, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_WHITE  = (255, 255, 255)
COLOR_ORANGE = (0, 165, 255)
COLOR_CYAN   = (255, 255, 0)

# ─────────────────────────────────────────
# DRAW CROSSHAIR AT CENTER
# ─────────────────────────────────────────
def draw_crosshair(frame, x, y):
    """Draw a fixed crosshair at the frame center."""
    size = 20
    thickness = 2

    # Horizontal line
    cv2.line(frame, (x - size, y), (x + size, y), COLOR_GREEN, thickness)
    # Vertical line
    cv2.line(frame, (x, y - size), (x, y + size), COLOR_GREEN, thickness)
    # Center dot
    cv2.circle(frame, (x, y), 4, COLOR_GREEN, -1)
    # Outer circle
    cv2.circle(frame, (x, y), LOCK_THRESHOLD, COLOR_GREEN, 1)

# ─────────────────────────────────────────
# DRAW ERROR VECTOR (ARROW)
# ─────────────────────────────────────────
def draw_error_vector(frame, center, marker_center):
    """Draw arrow from frame center to marker centroid."""
    cv2.arrowedLine(
        frame,
        center,           # start: frame center
        marker_center,    # end: marker position
        COLOR_YELLOW,     # color
        2,                # thickness
        tipLength=0.3     # arrowhead size
    )

# ─────────────────────────────────────────
# GET MOVEMENT COMMAND
# ─────────────────────────────────────────
def get_command(cx, cy, marker_x, marker_y):
    """
    Calculate movement command based on marker position
    relative to frame center.
    Returns command string and color.
    """
    dx = marker_x - cx   # positive = marker is RIGHT of center
    dy = marker_y - cy   # positive = marker is BELOW center

    # Check if locked (within threshold)
    if abs(dx) <= LOCK_THRESHOLD and abs(dy) <= LOCK_THRESHOLD:
        return "LOCK ENGAGED", COLOR_GREEN

    # Determine primary direction (which offset is larger)
    if abs(dx) > abs(dy):
        # Horizontal movement needed
        if dx > 0:
            return "MOVE RIGHT", COLOR_ORANGE
        else:
            return "MOVE LEFT", COLOR_ORANGE
    else:
        # Vertical movement needed
        if dy > 0:
            return "MOVE DOWN", COLOR_BLUE
        else:
            return "MOVE UP", COLOR_BLUE

# ─────────────────────────────────────────
# DRAW HUD (Heads Up Display)
# ─────────────────────────────────────────
def draw_hud(frame, command, color, dx, dy, marker_found):
    """Draw all on-screen information."""

    # Background bar at top
    cv2.rectangle(frame, (0, 0), (FRAME_WIDTH, 50), (0, 0, 0), -1)
    cv2.rectangle(frame, (0, 0), (FRAME_WIDTH, 50), (50, 50, 50), 1)

    if marker_found:
        # Command text (large, centered)
        font = cv2.FONT_HERSHEY_SIMPLEX

        # LOCK ENGAGED gets special treatment
        if command == "LOCK ENGAGED":
            cv2.rectangle(frame, (0, 0), (FRAME_WIDTH, 50), (0, 80, 0), -1)
            text_size = cv2.getTextSize(command, font, 1.0, 2)[0]
            text_x = (FRAME_WIDTH - text_size[0]) // 2
            cv2.putText(frame, command, (text_x, 35), font, 1.0, COLOR_GREEN, 2)
        else:
            text_size = cv2.getTextSize(command, font, 1.0, 2)[0]
            text_x = (FRAME_WIDTH - text_size[0]) // 2
            cv2.putText(frame, command, (text_x, 35), font, 1.0, color, 2)

        # Error offset info (bottom left)
        cv2.rectangle(frame, (0, FRAME_HEIGHT-35), (220, FRAME_HEIGHT), (0,0,0), -1)
        cv2.putText(frame, f"dx:{dx:+d}  dy:{dy:+d}",
                    (10, FRAME_HEIGHT - 10),
                    font, 0.6, COLOR_WHITE, 1)

        # Distance from center (bottom right)
        dist = int(np.sqrt(dx**2 + dy**2))
        cv2.putText(frame, f"dist: {dist}px",
                    (FRAME_WIDTH - 130, FRAME_HEIGHT - 10),
                    font, 0.6, COLOR_CYAN, 1)

    else:
        # No marker found
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "SEARCHING FOR MARKER...",
                    (120, 35), font, 0.8, COLOR_RED, 2)

    # Quit instruction
    cv2.putText(frame, "Press Q to quit",
                (FRAME_WIDTH - 150, FRAME_HEIGHT - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (150, 150, 150), 1)

# ─────────────────────────────────────────
# DRAW MARKER HIGHLIGHT
# ─────────────────────────────────────────
def draw_marker(frame, corners, marker_center, command):
    """Draw detected marker outline and center dot."""
    color = COLOR_GREEN if command == "LOCK ENGAGED" else COLOR_RED

    # Draw marker border
    pts = corners.reshape((-1, 1, 2)).astype(np.int32)
    cv2.polylines(frame, [pts], True, color, 2)

    # Draw marker center dot
    cv2.circle(frame, marker_center, 5, color, -1)

    # Label
    cv2.putText(frame, "TARGET",
                (marker_center[0] + 10, marker_center[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

# ─────────────────────────────────────────
# MAIN TRACKING LOOP
# ─────────────────────────────────────────
def main():
    print("=" * 50)
    print("  ArUco Marker Tracking System")
    print("=" * 50)
    print()
    print("  Starting webcam...")
    print("  Show ArUco marker (DICT_5X5_50, ID 0-49)")
    print("  to your webcam to begin tracking!")
    print()
    print("  Generate marker at: chev.me/aruco/")
    print("  Dictionary: 5x5 | Marker ID: 0")
    print()
    print("  Press Q to quit")
    print("=" * 50)

    # Open webcam
    cap = cv2.VideoCapture(0)

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("ERROR: Cannot open webcam!")
        print("Make sure your webcam is connected.")
        return

    print("\n  Webcam opened successfully!")

    # Set up ArUco detector
    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    aruco_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

    frame_center = (CENTER_X, CENTER_Y)

    print("  ArUco detector ready!")
    print("  Opening camera window...\n")

    while True:
        # Read frame from webcam
        ret, frame = cap.read()

        # Handle webcam failure gracefully (won't crash)
        if not ret:
            print("Warning: Failed to read frame, retrying...")
            continue

        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect ArUco markers
        corners, ids, rejected = detector.detectMarkers(gray)

        marker_found = False
        command = "SEARCHING..."
        cmd_color = COLOR_WHITE
        dx, dy = 0, 0

        if ids is not None and len(ids) > 0:
            # Marker detected!
            marker_found = True

            # Use the first detected marker
            corner = corners[0][0]

            # Calculate marker centroid (center point)
            marker_x = int(np.mean(corner[:, 0]))
            marker_y = int(np.mean(corner[:, 1]))
            marker_center = (marker_x, marker_y)

            # Calculate error (distance from frame center)
            dx = marker_x - CENTER_X
            dy = marker_y - CENTER_Y

            # Get movement command
            command, cmd_color = get_command(
                CENTER_X, CENTER_Y, marker_x, marker_y
            )

            # Draw marker outline
            draw_marker(frame, corner, marker_center, command)

            # Draw error vector arrow
            draw_error_vector(frame, frame_center, marker_center)

        # Always draw crosshair at center
        draw_crosshair(frame, CENTER_X, CENTER_Y)

        # Draw HUD (command text, info)
        draw_hud(frame, command, cmd_color, dx, dy, marker_found)

        # Show the frame
        cv2.imshow("ArUco Tracker — Disha", frame)

        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nQuitting...")
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("Tracking stopped. Goodbye!")


if __name__ == "__main__":
    main()