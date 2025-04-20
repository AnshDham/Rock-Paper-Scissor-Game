# Rock Paper Scissors Game using Python and OpenCV
import os
import cv2
import random
import time
from cvzone.HandTrackingModule import HandDetector
import cvzone

# Paths to resources
resource_folder = "Resources"
bg_image_path = os.path.join(resource_folder, "BG.png")

# Check if the resources folder and required files exist
if not os.path.exists(resource_folder):
    print(f"Error: Resources folder not found at {resource_folder}.")
    print("Please create the folder and add the required files (BG.png, 1.png, 2.png, 3.png).")
    exit(1)

if not os.path.exists(bg_image_path):
    print(f"Error: Background image not found at {bg_image_path}.")
    print("Please add BG.png to the Resources folder.")
    exit(1)

# Initialize the video capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

# Load the background image
original_bg = cv2.imread(bg_image_path)
imgbg = original_bg.copy()

# Initialize the hand detector
detector = HandDetector(maxHands=1)

# Initialize game variables
startGame = False
stateResult = False
timer = 0
score = [0, 0]  # [AI, Player]
ai_image_path = None
imgAi = None
previous_ai_move = None
result_text = ""

while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to capture video frame from the webcam.")
        break

    # Resize the captured image
    try:
        imgResized = cv2.resize(img, (640, 480))  # Resize to fixed dimensions
        imgCropped = imgResized[:, 80:560]  # Crop to match the game layout
    except Exception as e:
        print(f"Error during resizing or cropping: {e}")
        imgCropped = None

    # Detect hands
    if imgCropped is not None:
        hands, imgCropped = detector.findHands(imgCropped)
    else:
        hands = None
        print("Warning: Cropped image is None. Skipping this frame.")

    # Reset background to clear previous overlays
    imgbg = original_bg.copy()

    # Game logic
    if startGame:
        timer = time.time() - initialTime
        cv2.putText(imgbg, str(int(3 - timer)), (605, 465), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

        if timer > 3:
            timer = 0
            if hands:
                playerMove = None
                hand = hands[0]
                fingers = detector.fingersUp(hand)

                # Determine player move based on fingers
                if fingers == [0, 0, 0, 0, 0]:
                    playerMove = 1  # Rock
                elif fingers == [1, 1, 1, 1, 1]:
                    playerMove = 2  # Paper
                elif fingers == [0, 1, 1, 0, 0]:
                    playerMove = 3  # Scissors

                # AI move
                randomNumber = random.randint(1, 3)
                ai_image_path = os.path.join(resource_folder, f"{randomNumber}.png")
                imgAi = cv2.imread(ai_image_path, cv2.IMREAD_UNCHANGED)

                if imgAi is None:
                    print(f"Error: AI image not found at {ai_image_path}. Using a placeholder.")
                else:
                    # Overlay AI move image
                    imgbg = cvzone.overlayPNG(imgbg, imgAi, (149, 310))
                    previous_ai_move = imgAi

                # Determine winner
                if (playerMove == 1 and randomNumber == 3) or \
                   (playerMove == 2 and randomNumber == 1) or \
                   (playerMove == 3 and randomNumber == 2):
                    score[1] += 1  # Player scores
                    result_text = "Player Wins!"
                elif (playerMove == 3 and randomNumber == 1) or \
                     (playerMove == 1 and randomNumber == 2) or \
                     (playerMove == 2 and randomNumber == 3):
                    score[0] += 1  # AI scores
                    result_text = "AI Wins!"
                else:
                    result_text = "It's a Tie!"

                # Reset the game state to wait for the next round
                stateResult = True
                startGame = False

    # Display the AI move image and result message for a few seconds after the countdown
    if stateResult:
        if previous_ai_move is not None:
            imgbg = cvzone.overlayPNG(imgbg, previous_ai_move, (149, 310))
        if result_text:
            cv2.putText(imgbg, result_text, (480, 300), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 4)
        if time.time() - initialTime > 5:
            stateResult = False  # Reset for the next round
            result_text = ""

    if imgCropped is not None:
        try:
            imgbg[234:654, 795:1195] = cv2.resize(imgCropped, (400, 420))
        except Exception as e:
            print(f"Error placing cropped image on background: {e}")

    cv2.putText(imgbg, str(score[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgbg, str(score[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    try:
        cv2.imshow("BG", imgbg)
    except cv2.error as e:
        print(f"Error displaying the background image: {e}")
        break

    key = cv2.waitKey(1)
    if key == ord('s'):
        startGame = True
        initialTime = time.time()
        stateResult = False
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
