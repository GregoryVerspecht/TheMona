#Doel

6 wireless stations
met weemos D1 mini


## Test op terminal 1
mosquitto_sub -h 192.168.69.69 -t "test/topic"

## Test op terminal 2
mosquitto_pub -h 192.168.69.69 -t "test/topic" -m "Hallo MQTT!"
mosquitto_pub -h 192.168.69.69 -t "test/topic" -m "From the titty to the city!"


mosquitto_pub -h 192.168.69.69 -t "neopixel/set" -m '{"led":0, "r":255, "g":0, "b":0}'


mosquitto_pub -h 192.168.69.69 -t "neopixel/set" -m '{"led":3, "r":0, "g":0, "b":255, "brightness":128}'

##alle leds - kleur
mosquitto_pub -h 192.168.69.69 -t "neopixel/set" -m '{"all": true, "r":255, "g":0, "b":0, "brightness":128}'

##led x kleur met brightness
mosquitto_pub -h 192.168.69.69 -t "neopixel/set" -m '{"led":3, "r":0, "g":255, "b":0, "brightness":50}'

##Brightness alleen
mosquitto_pub -h 192.168.69.69 -t "neopixel/set" -m '{"brightness":200}'
