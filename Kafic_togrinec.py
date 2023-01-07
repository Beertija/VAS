#!/usr/bin/env python3
# -- coding: utf-8 --

import time, spade, argparse, json

parser = argparse.ArgumentParser(description='Radno vrijeme')
parser.add_argument('radno_vrijeme', type=int, help='Vrijeme u satima')
args = parser.parse_args()

konobari = {}
klijenti = []
cjenik = {"Piva":2.30, "Sok":1.5, "Bezalkoholno pivo":2, "Rakija":2.30}
skladiste = {"Piva":30, "Sok":10, "Bezalkoholno pivo":10, "Rakija":20}

class Kafic(spade.agent.Agent):
    class PorukeKonobara(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(10)
            if msg:
                message = json.loads(msg.body)
                if message["stanje"] == "start":
                    print(f"Dosao konobar: {message['jid']}")
                    konobari[message["jid"]] = "free"
                    print("Trenutni konobari: ", *konobari)
                elif message["stanje"] == "stanje":
                    if skladiste[message["pice"]] > 0:
                        skladiste[message["pice"]] -= 1
                        message_reply = {"jid":"beertija@localhost", "stanje":"ima", "cijena":cjenik[message["pice"]]}
                    else:
                        message_reply = {"jid":"beertija@localhost", "stanje":"nema"}
                    msg_reply = spade.message.Message(to = message["jid"], 
                                body = json.dumps(message_reply), 
                                metadata = {
                                    "ontology": "Konobar",
                                    "performative": "inform"
                                })
                    await self.send(msg_reply)
                elif message["stanje"] == "gotov":
                    self.agent.dobit += message["cijena"]
                    print(f"Za sada zaraden novac: {self.agent.dobit} €")
                    konobari[message["jid"]] = "free"
                    self.agent.zabiljezi = self.agent.ZabiljeziKonobara()
                    self.agent.add_behaviour(self.agent.zabiljezi)

    class PorukeKlijenata(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(10)
            if msg:
                message = json.loads(msg.body)
                if message["stanje"] == "dolazak":
                    if len(klijenti) > 5:
                        message_reply = {"jid":"beertija@localhost", "stanje":"pun"}
                    else:
                        klijenti.append(message["jid"])
                        message_reply = {"jid":"beertija@localhost", "stanje":"udi", "menu": cjenik}
                        self.agent.zabiljezi = self.agent.ZabiljeziKonobara()
                        self.agent.add_behaviour(self.agent.zabiljezi)
                    msg_reply = spade.message.Message(to = message["jid"], 
                                body = json.dumps(message_reply), 
                                metadata = {
                                    "ontology": "Klijent",
                                    "performative": "inform"
                                })
                    await self.send(msg_reply)

    class ZabiljeziKonobara(spade.behaviour.OneShotBehaviour):
        async def run(self):
            if klijenti:
                for x, y in konobari.items():
                    if y == "free":
                        konobari[x] = "busy"
                        message = {"jid":klijenti[0], "stanje":"klijent"}
                        klijenti.pop(0)
                        msg = spade.message.Message(to = x,
                                body = json.dumps(message),
                                metadata = {
                                    "ontology": "Konobar",
                                    "performative": "inform"
                                })
                        await self.send(msg)
                        print(f"poslano k {x} da posluzi")
                        break
                

    async def setup(self):
        self.dobit = 0
        template = spade.template.Template(metadata={"ontology": "Konobar"})
        template2 = spade.template.Template(metadata={"ontology": "Klijent"})
        poruke_konobara = self.PorukeKonobara()
        poruke_klijenata = self.PorukeKlijenata()
        self.add_behaviour(poruke_konobara, template)
        self.add_behaviour(poruke_klijenata, template2)
 
if __name__ == "__main__":
    vrijeme_rada = 1
    args.radno_vrijeme *= 60
    kafic = Kafic("beertija@localhost", "beertija")
    future = kafic.start()
    future.result()

    while vrijeme_rada < args.radno_vrijeme:
        try:
            vrijeme_rada += 1
            time.sleep(1)
        except KeyboardInterrupt:
            break

    kafic.stop()
    spade.quit_spade()
