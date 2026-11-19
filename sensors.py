# coded by aymane 
# this is the programme that i will be using to simulat the sensor
import random, time, json, os   
from datetime import datetime , timezone
import paho.mqtt.client as mqtt







# we will use dictionary to define 3 rooms
salles = {
    "salle1": {"occupation": "elevee", "exposition": "sud", "ventilation": "OFF"},
    "salle2": {"occupation": "moyenne", "exposition": "nord", "ventilation": "OFF"},
    "salle3": {"occupation": "faible", "exposition": "est", "ventilation": "OFF"},
}








def on_message( client, userdata, msg):
    try:
        salle = msg.topic.split("/")[1] # we will split the message comming from the whenever we found "/" and we chose the secend element with it referse to the room
        if salle in salles: # a condiotion to verifie if the rom sent by nod_red existe
            salles[salle]["ventilation"]=msg.payload.decode() # this methode is used to transforme  the message arrived from "octet" to a string
            # thise mean thet it will put on or of in the rooms[room][ventilation]
            print("roger command ->", salle, "ventilation :", salles[salle]["ventilation"])
    except Exception as e :
        print("not roger room not foude :" ,e)








#now we will creat the client mqtt that it could publish a message , receive a message , subscibe to a topic , or signale a connection probleme is the componant that is will contact the broker
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(
    os.getenv("MQTT_USER"), #set the user name from the envirenemnt fil to ensure the security 
    os.getenv("MQTT_PASSWORD")  #the same for the password
       )





# now we will config the last will
# we marque that thr last will is the a state conserved in the broker when the sensor is node diconected proprely
client.will_set(
    "smartenv/status",
    "offline",
    retain=True
) 





client.on_message = on_message # thise line tell the paho mqtt what function dit should call when a msg is arrived
client.connect("broker",1883) # connecting to the broker(the same name in docker compos ) o the port 1883
client.loop_start() # this is a loop is used to let the pricipale loop give data(simmulate the sensor)
client.subscribe("smartenv/+/ventilation") 
client.publish("smartenv/status", "online", retain= True)# thise commande publish the stat of the sensor we can use it like : Statut des capteurs : EN LIGNE





while True:
    for salle, info in salles.items():
        # Si ventilation ON -> les valeurs redescendent à la normale
        if info["ventilation"] == "ON":
            temperature = round(random.uniform(15, 20), 1)
            co2 = random.randint(300, 750)
        else:
            temperature = round(random.uniform(27, 35), 1)
            co2 = random.randint(690, 1200)
        humidite = random.randint(35, 70)

        # Message au format JSON (id, horodatage et valeurs)
        message = {
            "id": f"capteur_{salle}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "occupation": info["occupation"],
            "exposition": info["exposition"],
            "temperature": temperature,
            "humidite": humidite,
            "co2": co2,
            "ventilation": info["ventilation"]
        }

        client.publish(f"smartenv/{salle}/mesures", json.dumps(message))
        print(salle, "publie :", message)

    time.sleep(5)

