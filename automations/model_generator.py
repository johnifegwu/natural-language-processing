import csv
from faker import Faker
import random

# Initialize the Faker object
fake = Faker()

# Define a list of topics and their related fake companies
topic_company_map = {
    "Technology": [
        "TechCo", "InnovateX", "FutureTech", "CyberSolutions", "DataDyn", "NetWorks", "CodeWorks", "Bitwise", 
        "QuantumTech", "RoboSoft", "ByteForce", "NextGenTech", "AIventures", "CloudShift", "DevCom", "SmartTech", 
        "InfoSys", "Cybernetic", "EdgeLogic", "TechDrive"
    ],
    "Health": [
        "HealthCorp", "Medix", "WellnessPlus", "CareFirst", "BioHealth", "HealthTrack", "MediWorld", "LifeCare", 
        "VitalCare", "PureHealth", "OptiWell", "WellBeingHealth", "ReGenMed", "HealthQuest", "MediLife", 
        "Nutrify", "HealthEssentials", "WellMed", "HealthFlow", "MediSolutions"
    ],
    "Education": [
        "Learnify", "EduCenter", "BrightFuture", "ScholarHub", "KnowledgeBase", "EduWorld", "TeachFirst", 
        "BrainBridge", "SmartLearn", "InspireLearn", "NextGenEdu", "OpenAcademy", "StudyPro", "EduQuest", 
        "AcademiaX", "ThinkTank", "MindExpand", "EduAdvance", "Scholarly", "KnowledgeFlow"
    ],
    "Finance": [
        "FinTech", "WealthWise", "MoneyMatters", "InvestCorp", "SecureFinance", "AssetGrow", "CashFlow", 
        "CapitalGuard", "TrustFund", "ValueInvest", "AlphaFinance", "MoneyManager", "SafeInvest", "SmartWealth", 
        "PinnacleFinance", "FutureFunds", "EconSolutions", "WealthMax", "FinancialAdvantage", "FiscalSense"
    ],
    "Entertainment": [
        "StarMedia", "FilmWorld", "PlaytimeStudios", "EventPro", "FunHouse", "ShowBizCo", "SpotlightProductions", 
        "CineStar", "Entertainix", "MusicWave", "LiveArts", "ScreenPlay", "BigScreen", "PartyMasters", 
        "FestivalWorld", "StageLights", "RhythmPro", "VibeWorks", "FunTimePro", "EventMasters"
    ],
    "Science": [
        "ScienceLabs", "InnovativeResearch", "BioGen", "QuantumSolutions", "DiscoveryLabs", "FutureScience", 
        "BioFusion", "NanoTechLabs", "LabMasters", "ScienceCore", "BioWorks", "ResearchFirst", "DataScienceCo", 
        "BioMinds", "NextGenResearch", "LabSolutions", "QuantumResearch", "FutureLab", "ScienceVenture", 
        "BioInnovations"
    ],
    "Sports": [
        "FitLife", "Sportify", "AthleteHub", "ProSports", "ActiveWorld", "SportMax", "FitPro", "PlayHard", 
        "AthleteZone", "MoveNow", "EnduranceX", "SportFusion", "EliteAthletics", "PowerPlay", "ActiveFit", 
        "GameOn", "Athletico", "SportsNet", "PerformanceLab", "ProAthlete"
    ],
    "Politics": [
        "PoliDiscuss", "GovWatch", "CivicHub", "PolicyFirst", "NationBuilders", "PowerPolitics", "CivicSolutions", 
        "PolicyAdvocates", "PoliSphere", "NationTalk", "CivicLeaders", "GovernmentMatters", "GlobalGovernance", 
        "PolicyThinkers", "NationConnect", "PoliticalHub", "PublicPolicyCo", "CivicInsight", "GovAction", 
        "NationPulse"
    ]
}

# Generate 1000 unique records
training_data = []
for _ in range(1000):
    # Select a random topic
    topic = random.choice(list(topic_company_map.keys()))
    
    # Generate a random company name based on the topic
    company = random.choice(topic_company_map[topic])
    
    # Generate a random name
    name = fake.name()
    
    # Convert the name into a fake email address with the company domain
    first_name, last_name = name.split()[0].lower(), name.split()[-1].lower()  # use the first and last name
    email = f"{first_name}.{last_name}@{company.lower()}.com"
    
    # Append the record to the training_data list
    training_data.append({"name": name, "email": email, "topic": topic})

# Export the data to a CSV file
csv_file = "topic_training_data.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["name", "email", "topic"])
    writer.writeheader()
    writer.writerows(training_data)

print(f"CSV file '{csv_file}' with 1000 records has been created.")
