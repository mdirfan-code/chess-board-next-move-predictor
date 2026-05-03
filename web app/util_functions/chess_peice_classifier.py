
import numpy as np
import tensorflow as tf
from PIL import Image
import cv2

model = tf.keras.models.load_model('/mnt/d/Codes/ml-zone/projects/chess-board-next-move-predictor/machine learning/chess_piece_classification_model.h5')

# Define the piece types
piece_types = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
# Define image size
img_height, img_width = 128, 128

def predict_peice(image) :
    
    img = Image.fromarray(image, mode='L')
    img = img.resize((128, 128))
    
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 128, 128, 1)
    # Predict
    predictions = model.predict(img_array, verbose=0)
    
    # Get results
    predicted_class = int(np.argmax(predictions[0]))
    confidence = float(predictions[0][predicted_class])
    
    result = {
        'class': predicted_class,
        'confidence': confidence,
        'probabilities': predictions[0].tolist()
    }
    
    if piece_types and len(piece_types) > predicted_class:
        result['class_name'] = piece_types[predicted_class]
    
    return result

def identify_color_of_peice(ac_img, class_name):
    ret,ac_img = cv2.threshold(ac_img,190,255,cv2.THRESH_BINARY)
    # print(cell,"|",class_name)
    # print('---------------------------------------------------------------')
    
    split_percent = 20
    
    vert_l = ac_img.shape[0]
    hort_l = ac_img.shape[1]
    
    vert_split = (vert_l * split_percent)//100
    hort_split = (hort_l * split_percent)//100
    
    cnt = {0:0,255:0}
    for ik in ac_img[vert_split:-vert_split,hort_split:-hort_split]:
        for jk in ik:
            cnt[jk]+=1
            
    if cnt[0] > cnt[255]:
        # print("black_predicted")
        # print(ac_img[vert_split:-vert_split,hort_split:-hort_split])
        return  'black_' + class_name
    else:
        # print("white_predicted")
        # print(ac_img[vert_split:-vert_split,hort_split:-hort_split])
        return  'white_' + class_name 
    
    
if __name__ == "__main__":
    model = tf.keras.models.load_model('machine learning/chess_piece_classification_model.h5')
    # print(predict_piece('data/peices/king/img_b_king_24.jpg',model))

