#IMPORTS
import snippet as s
#RUN
result = s.get(
    uuid="27b192bb-58d2-4c09-aa16-eb3e04321006",
    engine='jade-001',
    variables={"var1":"Hello, World!"},
    timer=True
)
print(result)
