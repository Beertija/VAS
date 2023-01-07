#!/usr/bin/env python3
# -- coding: utf-8 --

import time, spade, argparse, json

parser = argparse.ArgumentParser(description='jid agenta')
parser.add_argument('jid', type=str, help='jid agenta konobar')
args = parser.parse_args()
 
class Konobar(spade.agent.Agent):
    class Initialize(spade.behaviour.FSMBehaviour):
         async def on_end(self):
            await self.agent.stop()
 
    class Pocetno(spade.behaviour.State):
        async def run(self):
            message = {"jid":args.jid, "stanje":"start"}
            msg = spade.message.Message(to = "beertija@localhost", 
                body = json.dumps(message), 
                metadata = {
                    "ontology": "Konobar",
                    "performative": "inform"
                })
            await self.send(msg)
            self.set_next_state("Cekanje")
 
    class Cekanje(spade.behaviour.State):
        async def run(self):
            msg = await self.receive(10)
            if msg:
                message = json.loads(msg.body)
                if message["stanje"] == "ima":
                    self.agent.cijena = message["cijena"]
                    self.set_next_state("Usluga")
                elif message["stanje"] == "nema":
                    self.set_next_state("Pitanje")
                elif message["stanje"] == "klijent":
                    self.agent.klijent = message["jid"]
                    self.set_next_state("Pitanje")
                elif message["stanje"] == "pice":
                    self.agent.pice = message["pice"]
                    self.set_next_state("Provjera")
            if not msg:
                self.set_next_state("Cekanje")
            
    class Usluga(spade.behaviour.State):
        async def run(self):
            message = {"jid":args.jid, "stanje":"racun", "cijena":self.agent.cijena}
            msg = spade.message.Message(to = self.agent.klijent, 
                body = json.dumps(message), 
                metadata = {
                    "ontology": "Konobar",
                    "performative": "inform"
                })
            await self.send(msg)
            message2 = {"jid":args.jid, "stanje":"gotov", "cijena":self.agent.cijena}
            msg2 = spade.message.Message(to = "beertija@localhost", 
                body = json.dumps(message2), 
                metadata = {
                    "ontology": "Konobar",
                    "performative": "inform"
                })
            await self.send(msg2)
            self.set_next_state("Cekanje")

    class Pitanje(spade.behaviour.State):
        async def run(self):
            message = {"jid":args.jid, "stanje":"narudzba"}
            msg = spade.message.Message(to = self.agent.klijent, 
                body = json.dumps(message), 
                metadata = {
                    "ontology": "Konobar",
                    "performative": "inform"
                })
            await self.send(msg)
            self.set_next_state("Cekanje")

    class Provjera(spade.behaviour.State):
        async def run(self):
            message = {"jid":args.jid, "stanje":"stanje", "pice":self.agent.pice}
            msg = spade.message.Message(to = "beertija@localhost", 
                body = json.dumps(message), 
                metadata = {
                    "ontology": "Konobar",
                    "performative": "inform"
                })
            await self.send(msg)
            self.set_next_state("Cekanje")
 
    class Gasenje(spade.behaviour.State):
        async def run(self):
            message = {"jid":args.jid, "stanje":"odjava"}
            msg = spade.message.Message(to = "beertija@localhost", 
                body = json.dumps(message), 
                metadata = {
                    "ontology": "Konobar",
                    "performative": "inform"
                })
            await self.send(msg)
 
    async def setup(self):
        fsm = self.Initialize()
        fsm.add_state("Pocetno", self.Pocetno(), True)
        fsm.add_state("Cekanje", self.Cekanje())
        fsm.add_state("Usluga", self.Usluga())
        fsm.add_state("Provjera", self.Provjera())
        fsm.add_state("Pitanje", self.Pitanje())
        fsm.add_state("Gasenje", self.Gasenje())
        fsm.add_transition("Pocetno", "Cekanje")
        fsm.add_transition("Cekanje", "Cekanje")
        fsm.add_transition("Cekanje", "Provjera")
        fsm.add_transition("Provjera", "Cekanje")
        fsm.add_transition("Cekanje", "Usluga")
        fsm.add_transition("Usluga", "Cekanje")
        fsm.add_transition("Cekanje", "Pitanje")
        fsm.add_transition("Pitanje", "Cekanje")
        fsm.add_transition("Cekanje", "Gasenje")
        self.add_behaviour(fsm)

if __name__ == "__main__":
    konobar = Konobar(args.jid, "konobar")
    future = konobar.start()
    future.result()

    while konobar.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    konobar.stop()
    spade.quit_spade()
