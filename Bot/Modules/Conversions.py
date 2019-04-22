import re
import math

from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message


def convert(message):
    # Convert Feet and inches to Kilograms
    match = re.search('([0-9,\.]+ ?)ft ?([0-9,\.]+ ?)in', message, flags=re.I) or \
            re.search('([0-9,\.]+ ?)\' ?([0-9,\.]+ ?)\'\'', message, flags=re.I)
    if match:
        feet, inches = float(match.group(1)), float(match.group(2))
        cm = (feet * 30.48) + (inches * 2.54)
        send_message(f"{feet} ft and {inches} in is {round(cm, 2)} cm!")
    else:
        # Convert Feet to cm
        match = re.search('([0-9,\.]+ ?)ft', message, flags=re.I) or \
                re.search('([0-9,\.]+ ?)\'', message, flags=re.I)
        if match:
            feet = float(match.group(1))
            cm = (feet * 30.48)
            send_message(f"{feet} ft is {round(cm, 2)} cm!")
        else:
            # Convert inch to cm
            match = re.search('([0-9,\.]+ ?)in', message, flags=re.I) or \
                    re.search('([0-9,\.]+ ?)\'\'', message, flags=re.I)
            if match:
                inch = float(match.group(1))
                cm = (inch * 2.54)
                send_message(f"{inch} in is {round(cm, 2)} cm!")
            # Convert Centimetres to Feet and inches
            else:
                match = re.search('([0-9,\.]+ ?)cm', message, flags=re.I)
                if match:
                    cm = float(match.group(1))
                    tempinches, feet = math.modf(cm * 0.03281)
                    inches = tempinches * 12
                    send_message(f"{cm} cm is {int(feet)}ft {round(inches, 1)}in!")
                else:
                    # Convert Stone to Kilograms
                    match = re.search('([0-9,\.]+ ?)lb', message, flags=re.I)
                    if match:
                        lb = float(match.group(1))
                        kg = lb * 0.45359237
                        send_message(f"{lb} lb is {round(kg, 2)} kg!")
                    else:
                        # Convert Kilograms to Stone
                        match = re.search('([0-9,\.]+ ?)kg', message, flags=re.I)
                        if match:
                            kg = float(match.group(1))
                            lb = kg / 0.45359237
                            send_message(f"{kg} kg is {round(lb, 2)} lb!")
                        else:
                            # Convert Miles to Kilimetres
                            match = re.search('([0-9,\.]+ ?)km', message, flags=re.I)
                            if match:
                                kilometres = float(match.group(1))
                                miles = kilometres * 1.609344
                                send_message(f"{kilometres} km is {round(miles, 2)} mi!")
                            else:
                                # Convert Kilometres to Miles
                                match = re.search('([0-9,\.]+ ?)mi', message, flags=re.I)
                                if match:
                                    miles = float(match.group(1))
                                    kilometres = miles / 1.609344
                                    send_message(f"{miles} mi is {round(kilometres, 2)} km!")
                                else:
                                    # Convert Fahrenheit to Celsius
                                    match = re.search('(-?[0-9,\.]+ ?)f', message, flags=re.I) or \
                                            re.search('(-?[0-9,\.]+ ?)°f', message, flags=re.I)
                                    if match:
                                        fahrenheit = float(match.group(1))
                                        celsius = (fahrenheit - 32) / 1.8
                                        send_message(f"{fahrenheit} °F is {round(celsius, 2)} °C!")
                                    else:
                                        # Convert Celsius to Fahrenheit
                                        match = re.search('(-?[0-9,\.]+ ?)c', message, flags=re.I) or \
                                                re.search('(-?[0-9,\.]+ ?)°c', message, flags=re.I)
                                        if match:
                                            celsius = float(match.group(1))
                                            fahrenheit = (celsius * 1.8) + 32
                                            send_message(f"{celsius} °C is {round(fahrenheit, 2)} °F!")
                                        else:
                                            # Convert Kelvin to Celsius
                                            match = re.search('(-?[0-9,\.]+ ?)k', message, flags=re.I) or \
                                                    re.search('(-?[0-9,\.]+ ?)°k', message, flags=re.I)
                                            if match:
                                                kelvin = float(match.group(1))
                                                celsius = kelvin - 273.15
                                                send_message(f"{kelvin} °K is {round(celsius, 2)} °C!")
                                            else:
                                                send_message(f"Unable to convert this. Unknown format or typo. "
                                                             f"Supported formats are: "
                                                             f"Mi, KM, °F, °C, °K, KG, lb, cm, ft and in.")
