import csv
import json
from deliverable2 import *

def test_url_validators():
    """Tests the URLValidator class by evaluating 100 sample webpages and saves the results to CSV."""
    # Initialize the URLValidator class with your SerpAPI key
    # Instantiate the URLValidator class
    validator = URLValidator(SerpAPI)
    
    sample_data = [
        ("I have just been on an international flight, can I come back home to hold my 1-month-old newborn?", "https://www.mayoclinic.org/healthy-lifestyle/infant-and-toddler-health/expert-answers/air-travel-with-infant/faq-20058539"),
        ("How does exercise affect mental health?", "https://www.psychologytoday.com/us/basics/mental-health/mental-health-treatment"),
        ("What are the benefits of drinking green tea?", "https://www.healthline.com/nutrition/top-10-evidence-based-health-benefits-of-green-tea"),
        ("What are the symptoms of COVID-19?", "https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html"),
        ("How can I improve my sleep quality?", "https://www.sleepfoundation.org/how-sleep-works/how-to-sleep-better"),
        ("What is the impact of social media on mental health?", "https://www.psychologytoday.com/us/blog/words-matter/202010/the-impact-of-social-media-on-mental-health"),
        ("How do I prevent heart disease?", "https://www.heart.org/en/healthy-living/healthy-lifestyle"),
        ("What are the side effects of too much caffeine?", "https://www.webmd.com/diet/caffeine-and-health"),
        ("How does meditation help with stress?", "https://www.headspace.com/meditation/stress"),
        ("What is the importance of hydration?", "https://www.medicalnewstoday.com/articles/290814"),
        ("What should I eat for a healthy breakfast?", "https://www.health.com/healthy-breakfast-ideas-4798168"),
        ("What are some effective time management techniques?", "https://www.mindtools.com/pages/main/newMN_HTE.htm"),
        ("What are the causes of back pain?", "https://www.mayoclinic.org/diseases-conditions/back-pain/symptoms-causes/syc-20369860"),
        ("How can I boost my immune system?", "https://www.healthline.com/nutrition/10-evidence-based-ways-to-improve-your-immune-system"),
        ("What are the benefits of yoga?", "https://www.yogajournal.com/lifestyle/health/benefits-of-yoga"),
        ("How does alcohol affect the body?", "https://www.niaaa.nih.gov/alcohol-health/overview-alcohol-consumption/what-are-the-effects-alcohol"),
        ("What are the different types of depression?", "https://www.psychologytoday.com/us/basics/depression/types-of-depression"),
        ("How can I reduce my risk of diabetes?", "https://www.cdc.gov/diabetes/prevention/index.html"),
        ("What is the role of fiber in digestion?", "https://www.webmd.com/diet/obesity/ss/slideshow-fiber-overview"),
        ("How do I manage anxiety?", "https://www.nimh.nih.gov/health/topics/anxiety-disorders"),
        ("What are the symptoms of depression?", "https://www.mentalhealth.org.uk/a-to-z/d/depression"),
        ("How do I know if I’m dehydrated?", "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/expert-answers/dehydration/faq-20058426"),
        ("What is the importance of exercise?", "https://www.cdc.gov/physicalactivity/basics/pa-health/index.htm"),
        ("What is a balanced diet?", "https://www.nhs.uk/live-well/eat-well/the-eatwell-guide/"),
        ("What is a healthy body weight?", "https://www.cdc.gov/healthyweight/assessing/bmi/index.html"),
        ("What is a healthy sleep routine?", "https://www.sleepfoundation.org/sleep-hygiene/healthy-sleep-tips"),
        ("How do I improve my memory?", "https://www.psychologytoday.com/us/basics/memory/10-tips-for-improving-your-memory"),
        ("What are the benefits of a plant-based diet?", "https://www.healthline.com/nutrition/top-5-health-benefits-of-plant-based-diet"),
        ("What are the symptoms of vitamin D deficiency?", "https://www.webmd.com/diet/obesity/ss/slideshow-vitamind-overview"),
        ("How does stress affect the body?", "https://www.psychologytoday.com/us/basics/stress/how-stress-affects-the-body"),
        ("What are some healthy ways to cope with stress?", "https://www.mentalhealth.org.uk/publications/how-to-cope-with-stress"),
        ("What are some common causes of headaches?", "https://www.mayoclinic.org/diseases-conditions/headache/symptoms-causes/syc-20351479"),
        ("What is intermittent fasting?", "https://www.healthline.com/nutrition/what-is-intermittent-fasting"),
        ("What are the best exercises for weight loss?", "https://www.health.com/fitness-workouts/lose-weight-fast-workouts-4798280"),
        ("How does smoking affect lung health?", "https://www.cdc.gov/tobacco/basic_information/health_effects/index.htm"),
        ("What is the difference between LDL and HDL cholesterol?", "https://www.heart.org/en/healthy-living/healthy-eating/eat-smart/fats/understanding-fats"),
        ("What is a healthy heart rate?", "https://www.cdc.gov/nchs/fastats/heart-disease.htm"),
        ("How do I reduce my sugar intake?", "https://www.healthline.com/nutrition/ways-to-reduce-sugar-intake"),
        ("What is a keto diet?", "https://www.healthline.com/nutrition/ketogenic-diet-101"),
        ("What are the risks of high blood pressure?", "https://www.cdc.gov/nchs/fastats/high-blood-pressure.htm"),
        ("How can I improve my digestion?", "https://www.webmd.com/digestive-disorders/digestive-health"),
        ("What is the role of antioxidants in the body?", "https://www.healthline.com/nutrition/antioxidants-explained"),
        ("How do I control my blood sugar?", "https://www.cdc.gov/diabetes/managing/index.html"),
        ("What is the best way to stay motivated?", "https://www.psychologytoday.com/us/blog/pieces-mind/201808/10-ways-to-stay-motivated"),
        ("How can I stay productive working from home?", "https://www.cnn.com/2020/03/23/success/working-from-home-tips/index.html"),
        ("What are the signs of burnout?", "https://www.psychologytoday.com/us/basics/burnout"),
        ("How do I manage my time effectively?", "https://www.mindtools.com/pages/main/newMN_HTE.htm"),
        ("What is mindfulness?", "https://www.mindful.org/what-is-mindfulness/"),
        ("How do I improve my self-esteem?", "https://www.psychologytoday.com/us/blog/self-esteem/201903/10-ways-to-boost-your-self-esteem"),
        ("How do I handle failure?", "https://www.psychologytoday.com/us/articles/200310/learning-to-learn-from-failure"),
        ("What are the benefits of journaling?", "https://www.psychologytoday.com/us/blog/saving-normal/201507/benefits-journaling"),
        ("What is the difference between introverts and extroverts?", "https://www.psychologytoday.com/us/articles/201207/the-science-of-introverts-vs-extroverts"),
        ("How can I develop a growth mindset?", "https://www.mindsetworks.com/science/"),
        ("What are the benefits of gratitude?", "https://www.psychologytoday.com/us/articles/201307/what-is-gratitude"),
        ("What is self-care?", "https://www.psychologytoday.com/us/blog/self-care-saturday/201907/what-is-self-care"),
        ("How do I stay positive?", "https://www.psychologytoday.com/us/articles/201208/positive-thinking"),
        ("How do I know if I am an empath?", "https://www.psychologytoday.com/us/articles/201504/11-signs-youre-empath"),
        ("What is social anxiety?", "https://www.psychologytoday.com/us/basics/anxiety/social-anxiety-disorder"),
        ("How do I overcome procrastination?", "https://www.psychologytoday.com/us/articles/201608/how-to-stop-procrastinating"),
        ("What is the best way to study?", "https://www.apa.org/education/k12/study-tips"),
        ("How do I set goals effectively?", "https://www.psychologytoday.com/us/articles/200701/goal-setting"),
        ("What is self-discipline?", "https://www.psychologytoday.com/us/articles/200906/self-discipline"),
        ("What is the importance of forgiveness?", "https://www.psychologytoday.com/us/articles/201604/the-power-forgiveness"),
        ("How do I deal with anxiety attacks?", "https://www.psychologytoday.com/us/articles/201509/how-to-deal-with-anxiety-attacks"),
        ("How do I improve my communication skills?", "https://www.psychologytoday.com/us/articles/201307/7-ways-to-improve-communication"),
        ("What is assertiveness?", "https://www.psychologytoday.com/us/articles/201801/what-is-assertiveness"),
        ("What is emotional intelligence?", "https://www.psychologytoday.com/us/basics/emotional-intelligence"),
        ("How do I build resilience?", "https://www.psychologytoday.com/us/articles/201307/7-ways-to-build-resilience"),
        ("How do I overcome perfectionism?", "https://www.psychologytoday.com/us/articles/201609/how-to-overcome-perfectionism"),
        ("What is the importance of sleep?", "https://www.psychologytoday.com/us/articles/201703/why-sleep-is-important"),
        ("What are some healthy habits?", "https://www.psychologytoday.com/us/articles/201707/5-simple-healthy-habits"),
        ("What is the difference between introverts and extroverts?", "https://www.psychologytoday.com/us/articles/201207/the-science-of-introverts-vs-extroverts"),
        ("How can I build self-confidence?", "https://www.psychologytoday.com/us/articles/200701/building-self-confidence"),
        ("What are the benefits of volunteering?", "https://www.psychologytoday.com/us/articles/201304/the-benefits-volunteering"),
        ("What is the importance of good posture?", "https://www.healthline.com/health/fitness-exercise/posture-tips"),
        ("How do I get better at public speaking?", "https://www.psychologytoday.com/us/articles/201504/how-to-get-better-at-public-speaking"),
        ("What is the importance of self-reflection?", "https://www.psychologytoday.com/us/articles/201809/self-reflection-the-power-thinking-about-yourself"),
        ("How can I find a good therapist?", "https://www.psychologytoday.com/us/therapists"),
        ("How can I manage my finances?", "https://www.investopedia.com/articles/personal-finance/092916/10-financial-tips-college-graduates.asp"),
        ("What is the difference between introverts and extroverts?", "https://www.psychologytoday.com/us/articles/201207/the-science-of-introverts-vs-extroverts"),
        ("How do I deal with rejection?", "https://www.psychologytoday.com/us/articles/201701/5-ways-to-deal-with-rejection"),
        ("What is the importance of mindfulness?", "https://www.psychologytoday.com/us/articles/201309/mindfulness-in-psychotherapy"),
        ("What are the symptoms of ADHD?", "https://www.cdc.gov/ncbddd/adhd/guidelines.html"),
        ("How do I deal with difficult people?", "https://www.psychologytoday.com/us/articles/201507/how-to-deal-with-difficult-people"),
        ("What is the importance of empathy?", "https://www.psychologytoday.com/us/articles/201707/the-importance-of-empathy"),
        ("How do I find purpose in life?", "https://www.psychologytoday.com/us/articles/201506/how-to-find-your-life-purpose"),
        ("How do I set boundaries?", "https://www.psychologytoday.com/us/articles/201707/how-to-set-healthy-boundaries"),
        ("How do I improve my work-life balance?", "https://www.psychologytoday.com/us/articles/201602/8-tips-for-improving-work-life-balance"),
        ("What is emotional abuse?", "https://www.psychologytoday.com/us/articles/201705/what-is-emotional-abuse"),
        ("How do I build a positive mindset?", "https://www.psychologytoday.com/us/articles/201710/building-a-positive-mindset"),
        ("What is the difference between sympathy and empathy?", "https://www.psychologytoday.com/us/articles/201510/what-sympathy-vs-empathy"),
        ("How do I stop negative thinking?", "https://www.psychologytoday.com/us/articles/201611/how-to-stop-negative-thinking"),
        ("What are the benefits of a morning routine?", "https://www.psychologytoday.com/us/articles/201701/why-a-morning-routine-can-make-you-happier"),
        ("What is self-sabotage?", "https://www.psychologytoday.com/us/articles/201803/how-stop-self-sabotage"),
        ("How can I cope with change?", "https://www.psychologytoday.com/us/articles/201802/how-to-cope-with-change"),
        ("What is the importance of goal-setting?", "https://www.psychologytoday.com/us/articles/201301/the-importance-of-setting-goals"),
        ("How can I deal with negative emotions?", "https://www.psychologytoday.com/us/articles/201304/how-to-manage-negative-emotions")
    ]

    
    # Create the CSV file and write the headers
    csv_file = "sample.csv"
    fieldnames = ["user_prompt", "url_to_check", "func_rating", "custom_rating"]
    
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        # Loop through 100 samples
        for prompt, url in sample_data:
            
            # Get the validation result by calling the rate_url_validity function
            result = validator.rate_url_validity(prompt, url)
            
            # Include the func_rating and custom_rating in the result
            result["user_prompt"] = prompt
            result["url_to_check"] = url
            
            # Save the result to the CSV
            writer.writerow({
                "user_prompt": prompt,
                "url_to_check": url,
                "func_rating": json.dumps(result["stars"]["score"]),
                "custom_rating": str(int(json.dumps(result["stars"]["score"]))+1),
            })
    
    print(f"CSV file saved to {csv_file}")

test_url_validators()
