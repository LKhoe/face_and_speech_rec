# import speech_recognition as sr
# #Funcao responsavel por ouvir e reconhecer a fala
# def ouvir_microfone():
#     #Habilita o microfone para ouvir o usuario
#     microfone = sr.Recognizer()
#     with sr.Microphone() as source:
#         #Chama a funcao de reducao de ruido disponivel na speech_recognition
#         microfone.adjust_for_ambient_noise(source)
#         #Avisa ao usuario que esta pronto para ouvir
#         print("Diga alguma coisa: ")
#         #Armazena a informacao de audio na variavel
#         audio = microfone.listen(source)
#     try:
#         #Passa o audio para o reconhecedor de padroes do speech_recognition
#         frase = microfone.recognize_sphinx(audio)
#         # frase = microfone.recognize_google(audio,language='pt-BR')
        
#         #Após alguns segundos, retorna a frase falada
#         print("Você disse: " + frase)
#     #Caso nao tenha reconhecido o padrao de fala, exibe esta mensagem
#     except sr.UnknownValueError:
#         print("Não entendi")
#         return frase

# #Chamada bloqueante            
# ouvir_microfone()


import speech_recognition as sr
import time

def callback(recognizer, audio):
    try:
        print("Google Speech Recognition thinks you said " + recognizer.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

# start listening in the background (note that we don't have to do this inside a `with` statement)
stop_listening = r.listen_in_background(m, callback)
# `stop_listening` is now a function that, when called, stops background listening

# do some unrelated computations for 5 seconds
for _ in range(5000): time.sleep(0.1)  # we're still listening even though the main thread is doing other things

# calling this function requests that the background listener stop listening
stop_listening(wait_for_stop=False)

# do some more unrelated things
while True: time.sleep(0.1)  # we're not listening anymore, even though the background thread might still be running for a second or two while cleaning up and stopping
