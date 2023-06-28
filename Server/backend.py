from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gtts import gTTS
import pygame
import os
from moviepy.editor import ImageSequenceClip

app = Flask(__name__)
CORS(app)

# Path to the frontend src folder from the backend.py file
frontend_src_path = os.path.join(os.path.dirname(__file__), '..', 'conversion', 'src')

# Font settings for the text overlay
font_path = os.path.join(frontend_src_path, 'font.ttf')
font_size = 32
font_color = (255, 255, 255)

@app.route('/')
def index():
    return "Welcome to the Text to Audio Video Converter API!"

@app.route('/api/convert', methods=['POST'])
def convert_text_to_video():
    # Get the text from the request payload
    text = request.json['text']

    # Convert text to speech
    output_file = os.path.join(frontend_src_path, 'output.mp4')
    convert_text_to_speech(text, output_file)

    # Initialize Pygame
    pygame.init()

    # Create the screen
    screen = pygame.display.set_mode((800, 600))  # Adjust the size as needed

    # Load frames
    frames = [
        pygame.image.load(os.path.join(frontend_src_path, 'av1.png')),
        pygame.image.load(os.path.join(frontend_src_path, 'av2.png')),
        pygame.image.load(os.path.join(frontend_src_path, 'av3.png')),
        pygame.image.load(os.path.join(frontend_src_path, 'av4.png')),
        pygame.image.load(os.path.join(frontend_src_path, 'av5.png'))
        # Add more frames as needed
    ]

    # Define sprite position and other properties
    x = 100
    y = 100
    current_frame = 0
    frame_counter = 0
    animation_speed = 60

    # Get the duration of the audio file
    audio_duration = pygame.mixer.Sound(output_file).get_length()

    # Play the audio file
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()

    # Get the start time of the animation
    start_time = pygame.time.get_ticks()

    # Create a list to store the frames for the video
    video_frames = []

    # Create a font object for text rendering
    font = pygame.font.Font(font_path, font_size)

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return jsonify({'message': 'Animation terminated'})

        # Clear the screen
        screen.fill((255, 255, 255))

        # Display the current frame of the avatar animation at its current position
        screen.blit(frames[current_frame], (x, y))

        # Render and display the text on the screen
        text_surface = font.render(text, True, font_color)
        screen.blit(text_surface, (10, 10))  # Adjust the text position as needed

        # Update the display
        pygame.display.update()

        # Update the animation frame
        frame_counter += 1
        if frame_counter >= animation_speed:
            current_frame = (current_frame + 1) % len(frames)
            frame_counter = 0

        # Check if the animation time exceeds the audio duration
        current_time = pygame.time.get_ticks()
        if current_time - start_time >= audio_duration * 1000:
            pygame.quit()
            # Save the frames as images
            for frame in video_frames:
                pygame.image.save(frame, os.path.join(frontend_src_path, 'frames', 'frame.png'))

            # Combine frames into a video using moviepy
            video_clip = ImageSequenceClip(os.path.join(frontend_src_path, 'frames'), durations=[1/animation_speed] * len(video_frames))
            video_path = os.path.join(frontend_src_path, 'output.mp4')
            video_clip.write_videofile(video_path, fps=animation_speed)

            # Return the video file
            return send_file(video_path, mimetype='video/mp4')

        # Append the current frame to the video frames
        video_frames.append(screen.copy())

def convert_text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)
    print("Speech saved successfully.")

if __name__ == '__main__':
    app.run()
