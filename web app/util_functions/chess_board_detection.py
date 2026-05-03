import cv2
import numpy as np
import matplotlib.pyplot as plt


def detect_and_transform_chessboard(image):
    """
    Detect a chessboard in an image and transform it to a square view.
    
    Args:
        image:  input image
    
    Returns:
        The warped (perspective-corrected) image of the chessboard
    """
    # Read the image
    img = image

    # Create a copy for visualization
    original = img.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    # thresh = cv2.adaptiveThreshold(
    #     gray,
    #     255,
    #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #     cv2.THRESH_BINARY,
    #     11,
    #     2
    # )
    edges = cv2.Canny(gray, 100, 200)
    thresh = edges
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by area
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 1000]
    
    # Sort contours by area (largest first)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
    # Find the contour with the closest shape to a square/rectangle
    chessboard_contour = None
    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
        
        # If the contour has 4 corners (likely a chessboard)
        if len(approx) == 4:
            chessboard_contour = approx
            break
    
    if chessboard_contour is None:
        # Try ChessboardCornerDetection as fallback method
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # Try with common chessboard sizes (internal corners)
        for pattern_size in [(7, 7), (8, 7), (7, 8), (8, 8)]:
            ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
            if ret:
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                # Find extremas to get the four outer corners
                points = corners.reshape(-1, 2)
                x_min, y_min = np.argmin(points.sum(axis=1)), np.argmin(np.diff(points, axis=1))
                x_max, y_max = np.argmax(points.sum(axis=1)), np.argmax(np.diff(points, axis=1))
                chessboard_contour = np.array([
                    points[x_min], points[y_min], 
                    points[x_max], points[y_max]
                ], dtype=np.int32)
                break
        
        if chessboard_contour is None:
            return "","","",False
    
    # Draw the contour on the original image for visualization
    cv2.drawContours(img, [chessboard_contour], 0, (0, 255, 0), 3)
    
    # Reshape the contour for perspective transform
    points = chessboard_contour.reshape(4, 2)
    
    # Order the points correctly: top-left, top-right, bottom-right, bottom-left
    rect = np.zeros((4, 2), dtype=np.float32)
    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]  # Top-left has smallest sum
    rect[2] = points[np.argmax(s)]  # Bottom-right has largest sum
    
    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]  # Top-right has smallest difference
    rect[3] = points[np.argmax(diff)]  # Bottom-left has largest difference
    
    # Now find the dimensions of the new image
    (tl, tr, br, bl) = rect
    
    # Calculate width
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    width = max(int(width_a), int(width_b))
    
    # Calculate height
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    height = max(int(height_a), int(height_b))
    
    # Ensure square output
    size = max(width, height)
    
    # Destination points for the perspective transform
    dst = np.array([
        [0, 0],             # Top-left
        [size - 1, 0],      # Top-right
        [size - 1, size - 1], # Bottom-right
        [0, size - 1]       # Bottom-left
    ], dtype=np.float32)
    
    # Calculate the perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(original, M, (size, size))
    
    return original, img, warped,True