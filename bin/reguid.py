import sys, re
sys.path.append("..")
import src.util.uuid

def load_file(filename):
	file=open(filename, "r")
	resource=file.read()
	file.close()
	return resource

def save_file(filename, value):
	file=open(filename, "w+")
	file.write(value)
	file.close()


type_guid = ["91a12281-c9a8-430a-8a2d-93903b4a264f","d2f1e70f-4582-459f-90a2-583bb10d1204","8a1650eb-17e5-4944-9e56-0a9817ce1665","315381b8-f3f1-496c-92be-b65ebdd6b8a1","b20c407a-2c83-4646-b64d-a82f5db26490","64c12e50-9069-471f-8cf5-e85667c7ba79","ee1fa76a-3114-4dac-9e0b-0b7320c085c7","81d947af-1548-4a96-a1e0-d8a4c67c6ec2","5c1b98df-8609-4660-83b2-44ec7b2e7611","3a9827f6-0dd5-4239-9544-6e42ef0085ce","76f84567-ca9a-45de-9bbb-d5f13ea6a154","753ea72c-475d-4a29-96be-71c522ca2097","92269b6e-4b6b-4882-852f-f7ef0e89c079","246a9164-487b-4f75-944b-2a6907b2b078","09d486c8-b1d5-4b9c-aac7-f5f179ddfb8a","9572fe01-bfa8-4763-9436-d7d6229e24ce","4f342579-febf-4018-84bb-7503a56f3687","81b8284b-0523-4b42-b38e-44fa99120edb","3ab7f926-5b29-4b2e-9992-575bd2caf760","34f6ee59-9c50-4503-97c1-86c4e86bd1b7","5be544cb-3d6b-4b75-ae79-b071fbe46094","8077aa1c-6762-4719-a6ea-fdfb0bcfa0c2","7029560a-ca17-4e32-a058-cf82b8facc33","6555559f-3092-49bd-8b91-ca15ba10a373","213f1e8c-8a3e-452b-af33-4ca3139fe960","5ec776c5-23f6-4098-a69d-600b08b220b0","410ce9c6-5ae0-4c66-9c2b-80b7470e2927","070b91d0-7e2d-4290-ba5e-1693a4d7181f","1d4ab0ff-e9cb-4f2d-8fb0-1d7e9f6f3280","1ff3f533-6156-42f6-9637-914770ccbb06","5e701a63-42d9-4a1c-b6ef-5df76d60d958","2330fe83-8cd6-4ed5-907d-11874e7ebcf4","7085bd26-e653-490b-908f-61208c260a86","0d36c35d-9508-440f-bfec-668f3db8cfeb","b4d7003d-be29-4459-870c-b1213be8d444","03741d38-c9f3-4526-acb9-71c7aa00b3b2","b6dbbed9-7e57-4ade-b1a3-be7fd218bb05","b4761bec-24e3-40fd-9983-14b7db257229","249e9ff2-865b-4683-a532-2ef356efbe04","ee605426-cfcb-4c07-bd97-4975b383052c","108fd7bf-d504-454c-91e5-a35cbeae748d","7ba9640c-40cb-44ec-9942-516d70a31c36","82a69b02-9fba-47d0-b206-6fd1769b0ebd","50a85e2f-80a1-4eb9-bf39-576c8999f260","7b39c919-de7f-4b77-b048-aae8bcf8edf5","6143c364-5931-441c-b234-c1043f18d80b","8948c66f-3e8b-4afc-8361-b0f4aeac8707","4858cfb6-735e-47be-b500-d63720fc4119","3de32e4a-1493-49c3-add7-ddf8738e1530","19a2a656-40f1-43ca-9eba-eb55d033b1d4","73a54f2e-4001-4676-93a0-804048a57081","1052fb85-22db-40e9-a4e1-5b1e1a3b2280","d07ae2ab-62fe-ff98-682a-abc15eb17f9c","823833ac-0f63-431c-82e7-0a502af21c65","5ac1e4ae-f849-4bf4-9b6c-316b30e7a5e6"]

try:
	xml=sys.argv[1]
	xml2=sys.argv[2]
except:
	sys.stdout.write("Incorrect parameters\n")
	sys.exit(0)

data = load_file(xml)

reobj = re.compile(r"\b[A-F0-9]{8}(?:-[A-F0-9]{4}){3}-[A-Z0-9]{12}\b", re.DOTALL | re.IGNORECASE)
result = reobj.findall(data)
for match in result:
	if match not in type_guid:
		new_guid = str(src.util.uuid.uuid4())
		print "%s was replaced %s"%(match,new_guid)
		data = data.replace(match, new_guid)

save_file(xml2,data)

