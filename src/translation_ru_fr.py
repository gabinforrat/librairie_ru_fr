"""
Fonction pour transcrire l'alphabet russe vers l'alphabet français. 
Utilise la transcription décrite ici: https://fr.wikipedia.org/wiki/Transcription_du_russe_en_fran%C3%A7ais

Args:
	string : Chaine de caractère original à transcrire vers l'alphabet français. 
Return:
	return_string : Nouvelle chaine de caractère transcrit dans l'alphabet français.

"""
def transcription_russe_vers_france(string : str=""):
	cpt = 0
	voyelle = {'А', 'Э', 'Ы', 'О', 'У', 'Я', 'Е', 'И', 'Ё', 'Ю', 'а', 'э', 'ы', 'о', 'у', 'я', 'е', 'и', 'ё', 'ю'} 
	return_string = ""
	for i in string:

		#А, а		
		if i == "А":
			return_string += "A"
		
		elif i == "а":
			return_string += "a"
		#Б, б		
		elif i == "Б":
			return_string += "B"
		
		elif i == "б":
			return_string += "b"
		#В, в		
		elif i == "В":
			return_string += "V"
		
		elif i == "в":
			return_string += "v"
		#Г, г		
		elif i == "Г":
			if cpt+1<len(string) and string[cpt+1] in {'Е','е','И','и','Ы','ы'} :
				return_string += "Gu"
			else :
				return_string += "G"
		elif i == "г":
			if cpt+1<len(string) and string[cpt+1] in {'Е','е','И','и','Ы','ы'} :
				return_string += "gu"
			else :
				return_string += "g"
		#Д, д		
		elif i == "Д":
			return_string += "D"
		
		elif i == "д":
			return_string += "d"
		#Е, е		
		elif i == "Е":

			#au début du mot après ь ou ъ
			if cpt==0 or string[cpt-1] in {" ","ь","ъ"}:
				return_string +="Ie"
			#après une voyelle autre que и ou й
			elif cpt>0 and string[cpt-1] in {'А', 'Э', 'Ы', 'О', 'У', 'Я', 'Е', 'Ё', 'Ю', 'а', 'э', 'ы', 'о', 'у', 'я', 'е', 'и', 'ё', 'ю'}:
				return_string += "Ïe"
			#après une consonne ou après un и ou un й
			else:
				return_string += "E"
		
		elif i == "е":
			#au début du mot après ь ou ъ
			if cpt==0 or string[cpt-1] in {" ","ь","ъ"}:
				return_string +="ie"
			#après une voyelle autre que и ou й
			elif cpt>0 and string[cpt-1] in voyelle and string[cpt-1] not in {'и','й','И','Й'}:
				return_string += "ïe"
			#après une consonne ou après un и ou un й
			else:
				return_string += "e"
		#Ё, ё		
		elif i == "Ё":
			return_string += "Io"
		
		elif i == "ё":
			return_string += "io"

		#Ж, ж		
		elif i == "Ж":
			return_string += "J"
		
		elif i == "ж":
			return_string += "j"

		#З, з		
		elif i == "З":
			return_string += "Z"
		
		elif i == "з":
			return_string += "z"

		#И, и		
		elif i == "И":
			if cpt>0 and string[cpt-1] in {'А', 'Э', 'Ы', 'О', 'У', 'Я', 'Е', 'Ё', 'Ю', 'а', 'э', 'ы', 'о', 'у', 'я', 'е', 'ё', 'ю'}:
				return_string += "Ï"
			else:
				return_string += "I"
		elif i == "и":
			if cpt>0 and string[cpt-1] in {'А', 'Э', 'Ы', 'О', 'У', 'Я', 'Е', 'Ё', 'Ю', 'а', 'э', 'ы', 'о', 'у', 'я', 'е', 'ё', 'ю'}:
				return_string += "ï"
			else:
				return_string += "i"

		#Й, й 		
		elif i == "Й":
			# mots finissant par ий ou  ый
			if cpt+1 == len(string) or string[cpt+1] == " ": #fin de mot
				if cpt>0 and string[cpt-1] in {'И','и','Ы','ы'}:
					return_string +=""
				else:
					return_string += "Ï"
			else:
				return_string += "Ï"
		
		elif i == "й":
			# mots finissant par ий ou  ый
			if cpt+1 == len(string) or string[cpt+1] == " ": #fin de mot
				if cpt>0 and string[cpt-1] in {'И','и','Ы','ы'}:
					return_string +=""
				else:
					return_string += "ï"
			else:
				return_string += "ï"

		#К, к		
		elif i == "К":
			return_string += "K"
		
		elif i == "к":
			return_string += "k"

		#Л, л		
		elif i == "Л":
			return_string += "L"
		
		elif i == "л":
			return_string += "l"

		#М, м		
		elif i == "М":
			return_string += "M"
		
		elif i == "м":
			return_string += "m"

		#Н, н		
		elif i == "Н":
			# en fin de mot après un и ou un ы
			if cpt+1 == len(string) or string[cpt+1] == " ": #fin de mot
				if cpt>0 and string[cpt-1] in {'И','и','Ы','ы'}:
					return_string +="Ne"
				else:
					return_string += "N"
			else:
				return_string += "N"
		
		elif i == "н":
			# en fin de mot après un и ou un ы
			if cpt+1 == len(string) or string[cpt+1] == " ": #fin de mot
				if cpt>0 and string[cpt-1] in {'И','и','Ы','ы'}:
					return_string +="ne"
				else:
					return_string += "n"
			else:
				return_string += "n"

		#О, о		
		elif i == "О":
			return_string += "O"
		
		elif i == "о":
			return_string += "o"

		#П, п		
		elif i == "П":
			return_string += "P"
		
		elif i == "п":
			return_string += "p"

		#Р, р		
		elif i == "Р":
			return_string += "R"
		
		elif i == "р":
			return_string += "r"

		#С, с		
		elif i == "С": 
			if cpt > 0 and cpt+1 < len(string) and string[cpt-1] in voyelle and string[cpt+1] in voyelle:
				return_string += "Ss"
			else:
				return_string += "S"
		elif i == "с":
			if cpt > 0 and cpt+1 < len(string) and string[cpt-1] in voyelle and string[cpt+1] in voyelle:
				return_string += "ss"
			else:
				return_string += "s"

		#Т, т		
		elif i == "Т":
			return_string += "T"
		
		elif i == "т":
			return_string += "t"

		#У, у 
		elif i == "У":
			return_string += "Ou"
		
		elif i == "у":
			return_string += "ou"

		#Ф, ф		
		elif i == "Ф":
			return_string += "F"
		
		elif i == "ф":
			return_string += "f"

		#Х, х		
		elif i == "Х":
			return_string += "Kh"
		
		elif i == "х":
			return_string += "kh"

		#Ц, ц		
		elif i == "Ц":
			return_string += "Ts"
		
		elif i == "ц":
			return_string += "ts"

		#Ч, ч		
		elif i == "Ч":
			return_string += "Tch"
		
		elif i == "ч":
			return_string += "tch"

		#Ш, ш		
		elif i == "Ш":
			return_string += "Ch"
		
		elif i == "ш":
			return_string += "ch"
		
		#Щ, щ
		elif i == "Щ":
			return_string += "Chtch"
		
		elif i == "щ":
			return_string += "chtch"

		#Ъ, ъ		
		elif i == "Ъ":
			return_string += ""
		
		elif i == "ъ":
			return_string += ""

		#Ы, ы		
		elif i == "Ы":
			return_string += "Y"
		
		elif i == "ы":
			return_string += "y"

		#Ь, ь		
		elif i == "Ь":
			return_string += ""
		
		elif i == "ь":
			return_string += ""

		#Э, э		
		elif i == "Э":
			return_string += "E"
		
		elif i == "э":
			return_string += "e"

		#Ю, ю		
		elif i == "Ю":
			if cpt>0 and string[cpt-1] in {'и','й','И','Й'}:
				return_string += "Ou"
			elif cpt>0 and string[cpt-1] in voyelle:
				return_string += "Ïou"
			else:
				return_string += "Iou"
		elif i == "ю":
			if cpt>0 and string[cpt-1] in {'и','й','И','Й'}:
				return_string += "ou"
			elif cpt>0 and string[cpt-1] in voyelle:
				return_string += "ïou"
			else:
				return_string += "iou"

		#Я, я		
		elif i == "Я":
			if cpt>0 and string[cpt-1] in {'и','й','И','Й'}:
				return_string += "A"
			elif cpt>0 and string[cpt-1] in voyelle:
				return_string += "Ïa"
			else:
				return_string += "Ia"
		
		elif i == "я":
			if cpt>0 and string[cpt-1] in {'и','й','И','Й'}:
				return_string += "a"
			elif cpt>0 and string[cpt-1] in voyelle:
				return_string += "ïa"
			else:
				return_string += "ia"

		#Other char
		else:
			return_string += i

		cpt += 1

	return return_string