import cv2


def remove_static_frames(input_video, output_video, movement_threshold=30):
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        print("Erro ao abrir o arquivo de vídeo.")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    _, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray_frame)
        _, diff_thresh = cv2.threshold(diff, movement_threshold, 255, cv2.THRESH_BINARY)

        if cv2.countNonZero(diff_thresh) > 0:
            out.write(frame)

        prev_gray = gray_frame

    cap.release()
    out.release()
    print(f"Vídeo processado salvo em: {output_video}")


remove_static_frames(r"C:\Users\paulo\Downloads\TEMP\GH010188.mp4", "output.mp4")
