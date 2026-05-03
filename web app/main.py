from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.responses import HTMLResponse
import cv2
import numpy as np
import tensorflow as tf
import time
from fastapi.templating import Jinja2Templates

# my functions
from util_functions.chess_board_detection import * # as detect_and_transform_chessboard
from util_functions.disect_chessboard import *
from util_functions.chess_peice_classifier import *
from util_functions.chess_solver import *
from util_functions.image_processing import *

app = FastAPI()

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# loading the classifier model



templates = Jinja2Templates(directory="templates")

@app.get("/template", response_class=HTMLResponse)
async def template_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "My Page",
        "user": "John",
        "items": ["Item 1", "Item 2"]
    })
    
cls_2_chb = {'white_pawn': 'P',
 'white_rook': 'R',
 'white_knight': 'N',
 'white_bishop': 'B',
 'white_queen': 'Q',
 'white_king': 'K',
 'black_pawn': 'p',
 'black_rook': 'r',
 'black_knight': 'n',
 'black_bishop': 'b',
 'black_queen': 'q',
 'black_king': 'k'}

@app.post("/process_frame")
async def process_frame(request: Request):
    start = time.time()
    body = await request.body()
    np_arr = np.frombuffer(body, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    detected_chessboard = []


    # thresh = cv2.Canny(gray, 100, 200, None, 3, False)
    # contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # # Draw all contours on the original image

    # cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

    # 1. Process image to get chess board.
    og,im, chessboard, detected = detect_and_transform_chessboard(frame)
    
    if detected:
        print("Chessboard detected!!!!")
        # 2. If found the chessboard then create a 8 x 8 grid of chess boxes with coordinates.
        edges_thresh_image, grid, gray_image = get_disected_grid(chessboard)
        # 3. Then will pass the individual chess grid one by one in the function to predict chess peice.
        vertical_file = ['8','7','6','5','4','3','2','1']
        horizontal_file = ['a','b','c','d','e','f','g','h']
        shred_offset = 10
        shred_offset_color = 20
        print(gray_image.shape)
        print("------------------ChessBoard---------------------")
        for i in range(8):
            rank_piece_pos = []
            for j in range(8):
                cell= horizontal_file[j]+vertical_file[i]
                posdict = grid[cell]
                image = edges_thresh_image[posdict['x1']+shred_offset:posdict['x2']-shred_offset,posdict['y1']+shred_offset:posdict['y2']-shred_offset]
                image2 = gray_image[grid[cell]['x1']+shred_offset_color:grid[cell]['x2']-shred_offset_color,grid[cell]['y1']+shred_offset_color:grid[cell]['y2']-shred_offset_color]
                sum_im = np.sum(image)
            
                if  sum_im < 1000:
                    class_name = 'empty_cell' 
                    print("[",cell,":",class_name,"]",end=" | ")
                    rank_piece_pos.append('.')
                else:
                    class_name = predict_peice(image)['class_name']
                    class_name = identify_color_of_peice(image2,class_name)
                    rank_piece_pos.append(cls_2_chb[class_name])
                    print("[",cell,":",class_name,"]",end=" | ")
                    
            detected_chessboard.append(rank_piece_pos+[])
        
        print("--------------------------------------------------")
        # 4. Once got the list of the classified peice set, create a chess board object and pass it to minimax algorithm to predict move.
        chess_obj = ChessBoard()
        chess_obj.board = detected_chessboard
        chess_obj.print_board()
        from_move, to_move = predict_best_move(chess_obj, is_white_turn=True, depth=3)
        
        
        # 5. Map the graphic of predicted move on board. 
        print(f"\nBest move for White: {from_move} -> {to_move}")
        
        x_start = ((grid[from_move]['x2']-grid[from_move]['x1'])//2)+grid[from_move]['x1']
        y_start = ((grid[from_move]['y2']-grid[from_move]['y1'])//2)+grid[from_move]['y1']
        
        x_end = ((grid[to_move]['x2']-grid[to_move]['x1'])//2)+grid[to_move]['x1']
        y_end = ((grid[to_move]['y2']-grid[to_move]['y1'])//2)+grid[to_move]['y1']
        # x_end = grid[from_move]['x1']
        # y_end = grid[from_move]['y1']
        
        # x_start = grid[to_move]['x1']
        # y_start = grid[to_move]['y1']
        start_point = [x_start,y_start][::-1]
        end_point = [x_end,y_end][::-1]
        cv2.arrowedLine(edges_thresh_image, start_point, end_point, 255, 5, tipLength=0.05)
        # Overlay text
        frame = edges_thresh_image
        # cv2.putText(frame, "chessboard detected!", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    # 1, (0, 255, 0), 2, cv2.LINE_AA)
     
        frame = draw_map_on_image(chessboard,frame)
        # frame = chessboard
        end = time.time()
        print("Time with chess board detection :",end-start)
    else:
        print("Chessboard not detected!")
        end = time.time()
        print("Time without chess board detection :",end-start)
    
    _, img_encoded = cv2.imencode('.jpg', frame)
    return Response(content=img_encoded.tobytes(), media_type="image/jpeg")
