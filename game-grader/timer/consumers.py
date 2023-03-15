import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .db_oprations import check_start_flag, updatePeriodStatus, flagstatus, updatePeriodincompleteduration, updatePeriodDuration, savestarttime,checkperiod, periodstarttime
from core.models import NewPlan
class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        print("inside",self.scope['user'])
        self.planid = self.scope["url_route"]["kwargs"]["id"]
        self.room_name = self.scope["user"].uuid
        print("---room name---",self.room_name)
        self.room_group_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        fstatus = await flagstatus(self.planid)
        # print("$$$$$$$$$$$$$$",flagstatus)
        if fstatus == True:
            data = await check_start_flag(self.planid)
            await self.send(text_data=data)
        else:
            pass

        await self.send(text_data=json.dumps({"message": "connection sucessfull....."}))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json["type"] == "start-clock":
            time = text_data_json["startTime"]
            timeobj = await savestarttime(self.planid, time)
            # flagcheck = await check_start_flag(self.planid)
            # print("-----#####-------",flagcheck)
            data = await check_start_flag(self.planid)
            await self.send(text_data=data)
            
        if text_data_json["type"] == "period-status":
            periodObj = await updatePeriodStatus(text_data_json)
        
        if text_data_json["type"] == "incompleteduration":
            await updatePeriodincompleteduration(text_data_json)

        if text_data_json["type"] == "periodData":
            periodDurationobj = await updatePeriodDuration(text_data_json)
            pass

        if text_data_json["type"] == "next-clock":
            print("~=~=~=~",text_data_json["id"])
            id = text_data_json["id"]
            checkperiodobj = await checkperiod(id)

        if text_data_json["type"] == "period-start-time":
            periodstarttimeobj = await periodstarttime(text_data_json)
            pass

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
    

    