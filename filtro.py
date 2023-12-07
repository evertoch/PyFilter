import cv2
import imutils

# Lista de imagens para os filtros
imagens_filtro = [
    cv2.imread('gorro.png', cv2.IMREAD_UNCHANGED),
    cv2.imread('rena.png', cv2.IMREAD_UNCHANGED),
    cv2.imread('2024.png', cv2.IMREAD_UNCHANGED)
]

# Índice do filtro atual
filtro_atual = 0

# Detector de rostos
classificador_faces = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def callback_mouse(event, x, y, flags, param):
    global filtro_atual
    if event == cv2.EVENT_LBUTTONDOWN:
        filtro_atual = (filtro_atual + 1) % len(imagens_filtro)

# Videostreaming ou vídeo de entrada
captura = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Configurar o callback do mouse
cv2.namedWindow('Filtros')
cv2.setMouseCallback('Filtros', callback_mouse)

while True:
    ret, quadro = captura.read()
    if not ret:
        break
    quadro = imutils.resize(quadro, width=1040)

    # Espelhar horizontalmente o frame
    quadro = cv2.flip(quadro, 1)

    # Detecção de rostos no frame
    faces = classificador_faces.detectMultiScale(quadro, 1.3, 5)

    for (x, y, w, h) in faces:
        # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Redimensionamento da imagem de entrada de acordo com a largura do rosto detectado
        imagem_redimensionada = imutils.resize(imagens_filtro[filtro_atual], width=w)
        filas_imagem = imagem_redimensionada.shape[0]
        col_imagem = w

        # Determinação de uma porção da altura da imagem de entrada redimensionada
        porcao_alto = filas_imagem // 4
        dif = 0

        # Se houver espaço suficiente sobre o rosto detectado para inserir a imagem redimensionada
        # A imagem será exibida nessa área
        if y + porcao_alto - filas_imagem >= 0:

            # Pegamos a seção do frame onde a imagem (gorro/tiara) será colocada
            quadro_secao = quadro[y + porcao_alto - filas_imagem: y + porcao_alto, x: x + col_imagem]
        else:
            # Determinamos a seção da imagem que excede a do vídeo
            dif = abs(y + porcao_alto - filas_imagem)
            # Pegamos a seção do frame onde a imagem (gorro/tiara) será colocada
            quadro_secao = quadro[0: y + porcao_alto, x: x + col_imagem]

         # Determinamos a máscara que a imagem de entrada redimensionada possui e também a invertemos
        mascara = imagem_redimensionada[:, :, 3]
        mascara_inv = cv2.bitwise_not(mascara)

        # Criamos uma imagem com fundo preto e a imagem (gorro/tiara/2021)
        # Em seguida, criamos uma imagem onde o fundo é o frame e a imagem (gorro/tiara/2021) é preta
        fundo_preto = cv2.bitwise_and(imagem_redimensionada, imagem_redimensionada, mask=mascara)
        fundo_preto = fundo_preto[dif:, :, 0:3]
        fundo_quadro = cv2.bitwise_and(quadro_secao, quadro_secao, mask=mascara_inv[dif:])

        # Somamos as duas imagens obtidas
        resultado = cv2.add(fundo_preto, fundo_quadro)
        if y + porcao_alto - filas_imagem >= 0:
            quadro[y + porcao_alto - filas_imagem: y + porcao_alto, x: x + col_imagem] = resultado
        else:
            quadro[0: y + porcao_alto, x: x + col_imagem] = resultado

     # Exibição do frame resultante
    cv2.imshow('Filtros', quadro)

    # Verificação se a tecla 'ESC' foi pressionada para encerrar o programa
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == 27:
        break

captura.release()
cv2.destroyAllWindows()
