from skillgap.services.resume_service import ResumeService

profile = ResumeService.process_resume("sample_data/resume.pdf")

print(profile)
print()
print(profile.skills)
print()
print(profile.education)
print()
print(profile.experience)