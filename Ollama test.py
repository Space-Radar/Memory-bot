from ollama import chat
from datetime import datetime
from difflib import SequenceMatcher
import json
import time
import os

KeepTalking = True
TimeStamp = ""
TimeToProcess = 0.00
ToAscii = ""
Debug = False


def is_similar(a, b, threshold=0.6): ## quantify how similar sentences are so that the ai can better interperate corrections
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > threshold # sequence matcher produces a ratio based on similarity of sentences

# Question management
    global KeepTalking
    query = str(input("Keep talking?: (Y/N) | "))
    if (query.upper() == "Y"): 
        os.system("cls")
        return ()
    elif (query.upper() == "N"):
        KeepTalking = False
        os.system("cls")
        return()
    else:
        print("Input not recognised: (Error 1) |")
        end_conversation()
 
def ask_question(): ## allows the user to input a question
    global Debug
    content = input("Ask Away: | ")
    if "MEMORY_WIPE_1982" in content:
        os.system("cls") # clear windows terminal
        memory_wipe()
        print("Memory wiped ... ")
        return ""  # prevent sending to model
    elif "DEBUG" in content:
        Debug = True
    return content

def process_question(content, messages): ## processes user question
    global elapsed
    global timestamp
    start = time.time()
    response = chat(model="TestModel_1",messages=messages + [{"role": "user", "content": content}])

    end = time.time()
    message = response["message"]
    text = message["content"]

    # CURRENT timestamp and processing time

    elapsed = end - start
    timestamp = datetime.now()

    # print dynamically if user wants debugging
    if Debug == True:
        print(f"{text} | elapsed: {elapsed} | processed at : {timestamp}")
    else:
        print(f"{text}")

    return message
   

# Memory management

def remember_response(question, response, timestamp, elapsed): ## stores the users input, bots response, timestamp and elapsed time
    memory = {
        "user": str(question),
        "assistant": response["content"],
        "timestamp": str(timestamp),
        "elapsed": float(elapsed),
    }

    with open("Memories.jsonl", "a", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False)
        f.write("\n")

def recall_memories():
    messages = []
    ts = datetime.now()
    with open("Memories.jsonl", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                memory = json.loads(line)
                user_content = memory.get("user", "")
                assistant_content = memory.get("assistant", "")
                
                # assistant_content += f" (response generated at {ts})"

                if Debug == True:
                    user_content += f" (asked at {ts}, response took {elapsed}s)" 
                
                messages.append({
                    "role": "user",
                    "content": user_content,
                })

                messages.append({
                    "role": "assistant",
                    "content": assistant_content,
                })

            except json.JSONDecodeError:
                continue
            # print(messages) # debug
    return messages

def memory_wipe():
    with open("Memories.jsonl", "w", encoding="utf-8", errors="ignore") as f:
        f.write("")
    f.close()

# Corrections and positive reinforcement

def store_correction(question, wrong_answer, correct_answer):
    correction = {
        "trigger": question.lower(),
        "wrong": wrong_answer,
        "correct": correct_answer
    }

    with open("Corrections.jsonl", "a", encoding="utf-8") as f:
        json.dump(correction, f, ensure_ascii=False)
        f.write("\n")

def load_corrections():
    corrections = []

    if not os.path.exists("Corrections.jsonl"):
        return corrections

    with open("Corrections.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                corrections.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return corrections

def apply_corrections(messages, user_question):
    corrections = load_corrections()
    system_notes = []

    for c in corrections:
        if is_similar(c["trigger"], user_question):
            system_notes.append(
                f"Correction note: Previously you answered '{c['wrong']}', "
                f"which is incorrect. The correct information is: {c['correct']}. "
                f"Do NOT repeat the incorrect answer."
            )

    if system_notes:
        messages = [{"role": "system", "content": "\n".join(system_notes)}] + messages

    return messages

    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > threshold

# what to do when conversing with the user 

def converse(): # how to process user input to print a response provided by the LLM
    messages = recall_memories()[-20:]
    question = ask_question()

    messages = apply_corrections(messages, question)

    response = process_question(question, messages)
    remember_response(question, response, timestamp, elapsed)

    # feedback loop
    feedback = input("Was this correct? (Y/N) | ").strip().upper()
    if feedback == "N":
        correct = input("What is the correct information? | ").strip()
        store_correction(question, response["content"], correct)

    end_conversation()

def end_conversation(): # if the user wants to end the conversation end conversation

    global KeepTalking
    query = str(input("Keep talking?: (Y/N) | "))
    if (query.upper() == "Y"): 
        os.system("cls")
        return ()
    elif (query.upper() == "N"):
        KeepTalking = False
        os.system("cls")
        return()
    else:
        print("Input not recognised: (Error 1) |")
        end_conversation()

# While the user wants to keep talking keep allowing them to prompt
while KeepTalking is True :
   os.system("cls")
   converse()

