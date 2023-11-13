import speech_recognition as sr
import re
import Adafruit_BBIO.GPIO as GPIO

def extract_specific_words(text, keyword_mappings):
    extracted_words = []
    # Extract numbers between 1 and 500 using regular expression
    numbers = [int(num) for num in re.findall(r'\b(?:[1-9]|[1-9][0-9]|[1-4][0-9][0-9]|500)\b', text)]

    # Convert numbers to binary and add to the extracted words
    for num in numbers:
        binary_representation = format(num, '08b')  # 8-bit binary representation
        extracted_words.append(("number", binary_representation))

    # Check for the entire phrase in keyword_mappings
    for keyword, binary_value in keyword_mappings.items():
        if keyword.lower() in text.lower():
            extracted_words.append((keyword, binary_value))

    return extracted_words

def turn_on_led(led_pin):
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.HIGH)

def turn_off_led(led_pin):
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.LOW)

def recognize_speech(keyword_mappings):
    recognizer = sr.Recognizer()

    while True:
        with sr.Microphone() as source:
            print("Say something...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=None)  # Set timeout to None for continuous listening

        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            print("You said: {}".format(text))

            extracted_words = extract_specific_words(text, keyword_mappings)
            if extracted_words:
                print("Extracted words: {}".format(extracted_words))

                # Loop through extracted words to control LEDs
                for word, value in extracted_words:
                    if word == "number":
                        # Use the value as needed
                        print("Number value: {}".format(value))
                    elif word in keyword_mappings:
                        # Turn on/off LEDs based on keyword
                        if value == "00000001":  # "open"
                            turn_on_led("P8_10")
                        elif value == "00000010":  # "close"
                            turn_on_led("P8_12")
                        elif value == "00000011":  # "light on"
                            turn_on_led("P8_14")
                        elif value == "00000100":  # "off"
                            turn_off_led("P8_16")
            else:
                print("No specific words found.")
        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")
        except sr.RequestError as e:
            print("Error with the request; {0}".format(e))

if __name__ == "__main__":
    # Specify the keyword mappings
    keyword_mappings = {
        "open": "00000001",
        "close": "00000010",
        "light on": "00000011",
        "off": "00000100"
    }

    # GPIO setup
    GPIO.setup("P8_10", GPIO.OUT)  # GPIO pin for LED1
    GPIO.setup("P8_12", GPIO.OUT)  # GPIO pin for LED2
    GPIO.setup("P8_14", GPIO.OUT)  # GPIO pin for LED3
    GPIO.setup("P8_16", GPIO.OUT)  # GPIO pin for LED4

    try:
        recognize_speech(keyword_mappings)
    finally:
        # Cleanup GPIO on exit
        GPIO.cleanup()

