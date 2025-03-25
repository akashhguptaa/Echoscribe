import os
from dotenv import load_dotenv
from google import genai
import re

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def get_summary(transcription):
    
    prompt = f"""
    Summarize the following video transcript in a descriptive way. 
    Include the main topics discussed, key points, and important takeaways.
    Format the summary with clear sections and bullet points where appropriate.
    
    TRANSCRIPT:
    {transcription}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

if __name__ == "__main__":
    test_transcript = "Marcus Mumford. Alright. Mumford and... songs. You ever had to spank any of them on stage. No. No. You make them call you dad. No. Too late One name it, Mufford and Sons, if you don't want to evoke. Fatherhood. Well, Americans don't understand this. but it's like what you call family business. businesses in the UK and call it something and science. Because usually it's the dad and their children. We run their business. Yes, I understand. It's both patriarchal. system but you know you try to bring politics in there Always man. Do you mind if we do a new segment sponsored by Cheeky Cheat? No, I do mind, yeah. And if I ask you something political? Okay fine, I'm not going to answer it. that problem. Just see if you mind it. And I have nothing. Okay cool. You know, temperature tech on you. They're at good. You lost 70 pounds? Yeah. What is that in dollars? F�리<|it|> E ne mettere Faccio Tiрезvi Bloчи Finca I had to stop eating ice cream. Do you feel like since you've lost the way you... become more mentally clear. Yeah, so you feel like you better understand how all of your fans. Wish you were still fat. No, I was a great time then. We said you were a fatter! That really fat. No really fat. I notice a lot of... funny actors. They lose and become less funny. That's interesting. But ignores- a lot of musicians, they lose weight. because they're on drugs. Will you say you're an act? a musician. Is this whole thing gonna be about my way? And you're going to make me sit here around all this ice cream just to serve. Test me. You hungry? You might be doing new seconds. presented by Shikashita. Do you have... something to do with Chica Chita. How do you know you're a big fan of it? Big fan is a peanut butter cure. Yeah, do you want me to? the blue guinea balls mind right now. Come on, do you know that market? This month, did the soundtrack for Ted Lasso. I didn't know that. I loved 10 last, so I forgot about that. Yeah! Skip and try. You ever look out into the crowd when you're performing at a festival? He'd be like every single person here. sharing the same five portaplates. No, don't worry about that. I've watched a lot of... of music documentaries. I like music. Yeah. I like it a lot. Yeah. Every documentary about successful b- The band starts. They're having a lot of fun. People like their music. They get really successful. They go to happy. huge egos and hate each other. What part of you guys at? We're in the successful part of space. And your ego's gonna get bigger than this. Yeah, yeah. Are you one of those guys who plans in your set to have an encore. Yeah, it's a big... For Sard, I think people are caught oning on at this point. Have you ever... been on a show where they didn't request an encore. Really? Yes, sir. Did you still go out and perform it? No, we have done that as well. Outstate- welcome for sure. Really? Yeah, I'm going to play it in the... another house. really travel the globe with this thing. Yeah, I mean you played everywhere, you traveled the globe. Yeah. Can I ask you a question? I think all of us guys want to know. Go on. What are the that it's normalized for the... girls in the beaches to be taught. France. That's right. Italy, Italy, but... span. Can do a fault question. from also our skies place. Would it be... weird for us to go to the top of the speech but keep our shirts on. You wanna be there? We also have a lot of African American fans. Can I ask a question for them? Is it okay if they go to the top of the... beach and keep their shoes on. We have a lot of African-American fans. I don't know how you guys get away with this shit. Tell me about your wife. You hate her yet? Okay. I love my wife. And you fell in love with her, but... writing her letters. Yep, she was in prison. That we're at Bob. camera which is similar in lots of ways but yeah pin it out. Yes sir. How do you guys think of this? You take a photo Are you insane, the fudder? No, but she has still got some of the letters and they're quite bad. Was it before after your fat? You have a signature emoji you send? Like you know this Texas from Markis Month for because he sent it. I like this one. Out one. Give it an intro. No, I'm dying, I see. Can I have your phone number? Born in the USA, yes sir. That song is about you. It is, I've always considered that my song. But being a- citizen for real. Is that affected you? Anyway at all, you don't go f*** you to rich I don't care about your... No, I fight. Yeah, really? Yeah, what'd you vote for? It's a rumor but did you hear the rumor that Joe bought? was alive the entire time. Sorry, cause it was important to remove the Would you give up one of your citizenships since you have to these hot ass latinas we're having in the pool. What? What? What? Is it a shame? Oh Lord, then I hate. get away with this."
    print(get_summary(test_transcript))