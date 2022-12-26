"""
For finding the face and face landmarks for further manipulication
"""

import cv2
import mediapipe as mp
import numpy as np

class FaceMeshDetector:
    def __init__(self,
                 static_image_mode=False,
                 max_num_faces=1,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):

        self.static_image_mode = static_image_mode
        self.max_num_faces = max_num_faces
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        # Facemesh
        self.mp_face_mesh = mp.solutions.face_mesh
        # The object to do the stuffs
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            self.static_image_mode,
            self.max_num_faces,
            True,
            self.min_detection_confidence,
            self.min_tracking_confidence
        )

        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(color=[224, 224, 224], thickness=1, circle_radius=1)

        # facial keypoints
        mouth = [0, 61, 17, 291, 13, 14]
        nose = [122, 351, 48, 4, 278, 2]
        cheek_r = [50, 206, 192]
        cheek_l = [280, 426, 416]
        eye_r = [133, 159, 130, 145]
        eye_l = [362, 386, 359, 374]
        eyebrow_r = [107, 105, 46]
        eyebrow_l = [336, 334, 276]

        iris_r = [473]
        iris_l = [468]
        self.kp_list = mouth + nose + cheek_r + cheek_l + eye_r + iris_r + eye_l + iris_l + eyebrow_r + eyebrow_l


    def findFaceMesh(self, img, img_size=(480, 640), draw=True):
        # convert the img from BRG to RGB
        img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        img.flags.writeable = False
        self.results = self.face_mesh.process(img)

        # Draw the face mesh annotations on the image.
        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        self.imgH, self.imgW, self.imgC = img.shape

        self.faces = []
        tmp = [] # for emotion
        if self.results.multi_face_landmarks:
            for face_landmarks in self.results.multi_face_landmarks:
                if draw:
                    self.mp_drawing.draw_landmarks(
                        image = img,
                        landmark_list = face_landmarks,
                        connections = self.mp_face_mesh.FACEMESH_TESSELATION, # FACEMESH_CONTOURS, # FACEMESH_TESSELATION,
                        landmark_drawing_spec = self.drawing_spec,
                        connection_drawing_spec = self.drawing_spec)

                face = []
                
                for id, lmk in enumerate(face_landmarks.landmark):
                    x, y = int(lmk.x * self.imgW), int(lmk.y * self.imgH)
                    face.append([x, y])

                    # show the id of each point on the image
                    # cv2.putText(img, str(id), (x-4, y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)

                    """ for Emotion"""
                    if id in self.kp_list:
                        tmp.append([lmk.x, lmk.y, lmk.z])
                        x = int(lmk.x * img_size[1])
                        y = int(lmk.y * img_size[0])
                        # cv2.circle(annotated_image, (x, y), radius=3, color=(0, 0, 255), thickness=1)


                self.faces.append(face)

        return img, self.faces, np.array(tmp)


# sample run of the module
def main():

    detector = FaceMeshDetector()

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, img = cap.read()

        if not success:
            print("Ignoring empty camera frame.")
            continue

        img, faces = detector.findFaceMesh(img)

        # if faces:
        #     print(faces[0])

        cv2.imshow('MediaPipe FaceMesh', img)

        # press "q" to leave
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()


if __name__ == "__main__":
    # demo code
    main()
