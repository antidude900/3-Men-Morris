
while True:
	try:
		mode=str(input("Which mode do you want to play?\nClick 'p' for pass and play\n'l' for local multiplayer\n'm' for multiplayer:"))
		
	except:
		print("\nInvalid Input!\n")

	else:
		if mode.lower() in ["p","l"]:
			break

		elif mode.lower() == "m":
			print("\nSorry no online server has been rented. So though the code is completed cant be played. However the local multiplayer and pass and play are available to play!\n")

		else:
			print("\nInvalid Input!\n")

print("\nPlease Wait....\n")

if mode.lower()=='p':
	import Pass_and_Play

elif mode.lower()=='l':
	import Local_Multiplayer







