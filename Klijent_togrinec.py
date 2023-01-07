#!/usr/bin/env python3
# -- coding: utf-8 --

import time, spade, json, random

class Klijent(spade.agent.Agent):
    class Initialize(spade.behaviour.FSMBehaviour):
         async def on_end(self):
            await self.agent.stop()
 
    class Pocetno(spade.behaviour.State):
        async def run(self):
            message = {"jid":self.agent.name + "@localhost", "stanje":"dolazak"}
            msg = spade.message.Message(to = "beertija@localhost", 
                body = json.dumps(message), 
                metadata = {
                    "ontology": "Klijent",
                    "performative": "inform"
                })
            await self.send(msg)
            self.set_next_state("Cekanje")
 
    class Cekanje(spade.behaviour.State):
        async def run(self):
            msg = await self.receive(10)
            if msg:
                message = json.loads(msg.body)
                if message["stanje"] == "pun":
                    print("Kafic je prepun")
                    self.set_next_state("Gasenje")
                elif message["stanje"] == "udi":
                    print(f"Bok ljudi, ja doso - {self.agent.name}")
                    self.agent.menu = message["menu"]
                    print("Cjenik za klijenta: ", *self.agent.menu)
                    self.set_next_state("Cekanje")
                elif message["stanje"] == "narudzba":
                    self.agent.konobar = message["jid"]
                    self.set_next_state("Pitanje")
                elif message["stanje"] == "racun":
                    self.agent.cijena = message["cijena"]
                    self.set_next_state("Racun")
            if not msg:
                self.set_next_state("Cekanje")

    class Pitanje(spade.behaviour.State):
        async def run(self):
            message = {"jid":self.agent.name + "@localhost", "stanje":"pice", "pice": random.choice(list(self.agent.menu.keys()))}
            msg = spade.message.Message(to = self.agent.konobar, 
                body = json.dumps(message), 
                metadata = {
                    "ontology": "Klijent",
                    "performative": "inform"
                })
            await self.send(msg)
            self.set_next_state("Cekanje")

    class Racun(spade.behaviour.State):
        async def run(self):
            print(f"{self.agent.name}@localhost je platio racun.")
            self.set_next_state("Gasenje")
 
    class Gasenje(spade.behaviour.State):
        async def run(self):
            print("Izlazak iz kafica")
 
    async def setup(self):
        fsm = self.Initialize()
        fsm.add_state("Pocetno", self.Pocetno(), True)
        fsm.add_state("Cekanje", self.Cekanje())
        fsm.add_state("Pitanje", self.Pitanje())
        fsm.add_state("Racun", self.Racun())
        fsm.add_state("Gasenje", self.Gasenje())
        fsm.add_transition("Pocetno", "Cekanje")
        fsm.add_transition("Cekanje", "Cekanje")
        fsm.add_transition("Cekanje", "Pitanje")
        fsm.add_transition("Pitanje", "Cekanje")
        fsm.add_transition("Cekanje", "Racun")
        fsm.add_transition("Racun", "Gasenje")
        fsm.add_transition("Cekanje", "Gasenje")
        self.add_behaviour(fsm)

if __name__ == "__main__":
    for i in range(100):
        k = Klijent("k" + str(i) + "@localhost", "kupac")
        k.start()
        time.sleep(1)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    klijent.stop()
    spade.quit_spade()
