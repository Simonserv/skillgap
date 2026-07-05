document.addEventListener("DOMContentLoaded", () => {
    // API Base URL
    const API_URL = ""; // Relative path works since FastAPI serves us from root

    // Application State
    let resumeProfile = null;
    let jobListings = [];
    let selectedJob = null;
    let currentAnalysis = null;
    let checkedSkills = new Set();

    // DOM Elements
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");
    const uploadStatus = document.getElementById("upload-status");
    const profilePreview = document.getElementById("profile-preview");
    const profileName = document.getElementById("profile-name");
    const profileEmail = document.getElementById("profile-email");
    const profileSummary = document.getElementById("profile-summary");
    const profileSkillsNum = document.getElementById("profile-skills-num");

    const searchCard = document.getElementById("search-card");
    const searchInput = document.getElementById("search-input");
    const searchBtn = document.getElementById("search-btn");
    const jobList = document.getElementById("job-list");
    const jobSearchStatus = document.getElementById("job-search-status");

    const matchPlaceholder = document.getElementById("match-placeholder");
    const matchingStatus = document.getElementById("matching-status");
    const matchReport = document.getElementById("match-report");

    const jobDetailTitle = document.getElementById("job-detail-title");
    const jobDetailCompany = document.getElementById("job-detail-company");
    const jobDetailSource = document.getElementById("job-detail-source");

    const readinessScoreNum = document.getElementById("readiness-score-num");
    const progressBar = document.getElementById("progress-bar");
    const projectedBadge = document.getElementById("projected-badge");
    const projectedScoreNum = document.getElementById("projected-score-num");

    const scoreSemantic = document.getElementById("score-semantic");
    const fillSemantic = document.getElementById("fill-semantic");
    const scoreSkills = document.getElementById("score-skills");
    const fillSkills = document.getElementById("fill-skills");
    const scoreExperience = document.getElementById("score-experience");
    const fillExperience = document.getElementById("fill-experience");
    const expExplanation = document.getElementById("exp-explanation");

    const gapsList = document.getElementById("gaps-list");
    const roadmapList = document.getElementById("roadmap-list");
    const overlappingSkillsList = document.getElementById("overlapping-skills-list");

    // Circular progress perimeter: 2 * PI * radius = 2 * 3.14159 * 60 = 377
    const CIRCLE_CIRCUMFERENCE = 377;

    // --- drag and drop upload handlers ---
    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Upload PDF to backend API
    async function handleFileUpload(file) {
        if (file.type !== "application/pdf") {
            alert("Please upload a PDF resume file.");
            return;
        }

        uploadStatus.classList.remove("hidden");
        profilePreview.classList.add("hidden");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch(`${API_URL}/api/profile/upload`, {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Failed to parse resume.");
            }

            resumeProfile = await res.json();
            renderProfile(resumeProfile);

            // Unlock Job Search
            searchCard.classList.remove("disabled");
            searchInput.removeAttribute("disabled");
            searchBtn.removeAttribute("disabled");

        } catch (err) {
            alert(`Error: ${err.message}`);
        } finally {
            uploadStatus.classList.add("hidden");
        }
    }

    function renderProfile(profile) {
        profileName.textContent = profile.name || "Resume Profile";
        profileEmail.textContent = profile.email || "";
        profileSummary.textContent = profile.summary || "No summary extracted.";
        
        // Count skills
        let skillNames = [];
        if (profile.skills) {
            if (Array.isArray(profile.skills)) {
                skillNames = profile.skills;
            } else if (typeof profile.skills === 'object') {
                // Flatten skills dictionary
                const flatten = (obj) => {
                    let acc = [];
                    for (let k in obj) {
                        acc.push(k);
                        if (Array.isArray(obj[k])) acc.push(...obj[k]);
                        else if (typeof obj[k] === 'object') acc.push(...flatten(obj[k]));
                    }
                    return acc;
                };
                skillNames = flatten(profile.skills);
            }
        }
        
        // Deduplicate
        const uniq = [...new Set(skillNames.map(s => s.trim().toLowerCase()))].filter(Boolean);
        profileSkillsNum.textContent = uniq.length;
        profilePreview.classList.remove("hidden");
    }

    // --- job search handlers ---
    searchBtn.addEventListener("click", performJobSearch);
    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") performJobSearch();
    });

    async function performJobSearch() {
        const keyword = searchInput.value.trim();
        if (keyword.length < 2) {
            alert("Search keyword must be at least 2 characters.");
            return;
        }

        jobSearchStatus.classList.remove("hidden");
        jobList.innerHTML = "";

        try {
            const res = await fetch(`${API_URL}/api/jobs/search`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    keyword: keyword,
                    profile: resumeProfile
                })
            });
            if (!res.ok) throw new Error("Failed to scan job market.");

            jobListings = await res.json();
            
            // Sort by readiness score descending if available
            if (resumeProfile && jobListings.length > 0 && jobListings[0].readiness_score !== undefined) {
                jobListings.sort((a, b) => (b.readiness_score || 0) - (a.readiness_score || 0));
            }

            renderJobListings(jobListings);
        } catch (err) {
            jobList.innerHTML = `<p class="placeholder-text" style="color: #ef4444;">Error searching market: ${err.message}</p>`;
        } finally {
            jobSearchStatus.classList.add("hidden");
        }
    }

    function renderJobListings(jobs) {
        if (jobs.length === 0) {
            jobList.innerHTML = '<p class="placeholder-text">No jobs found matching your search. Try another keyword.</p>';
            return;
        }

        jobList.innerHTML = "";
        jobs.forEach((job, index) => {
            const jobItem = document.createElement("div");
            jobItem.className = "job-item";
            jobItem.dataset.index = index;

            // Render score badge if available
            let matchBadgeHtml = "";
            let bestFitBadgeHtml = "";
            
            if (job.readiness_score !== null && job.readiness_score !== undefined) {
                const score = Math.round(job.readiness_score);
                const scoreClass = score >= 70 ? "high" : (score >= 45 ? "mid" : "low");
                matchBadgeHtml = `<span class="match-pill ${scoreClass}">${score}% Match</span>`;
                
                // Highlight the absolute best matching job
                if (index === 0 && score > 0) {
                    jobItem.classList.add("best-fit");
                    bestFitBadgeHtml = `<span class="best-fit-tag">★ Best Fit</span>`;
                }
            }

            jobItem.innerHTML = `
                <div class="job-title-row" style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; width: 100%;">
                    <h4 style="margin: 0; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${job.title}</h4>
                    <div style="display: flex; align-items: center; gap: 0.35rem; flex-shrink: 0;">
                        ${bestFitBadgeHtml}
                        ${matchBadgeHtml}
                    </div>
                </div>
                <div class="job-company" style="margin-top: 0.25rem;">${job.company}</div>
                <div class="job-meta-row">
                    <span>${job.location || 'Remote'}</span>
                    <span>${job.source}</span>
                </div>
            `;

            jobItem.addEventListener("click", () => {
                // Highlight item
                document.querySelectorAll(".job-item").forEach(item => item.classList.remove("selected"));
                jobItem.classList.add("selected");
                
                // Load Gap Analysis
                selectedJob = job;
                calculateGap(job);
            });

            jobList.appendChild(jobItem);
        });
    }

    // --- gap analysis & matching ---
    async function calculateGap(job) {
        matchPlaceholder.classList.add("hidden");
        matchReport.classList.add("hidden");
        
        // If the job has no skills extracted yet, show the unenriched view
        if (!job.skills || job.skills.length === 0) {
            renderUnenrichedJob(job);
            return;
        }

        matchingStatus.classList.remove("hidden");

        try {
            matchingStatus.querySelector("span").textContent = "Calculating JobMatch scores & loading course roadmap...";
            const matchRes = await fetch(`${API_URL}/api/match`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    profile: resumeProfile,
                    job: job
                })
            });

            if (!matchRes.ok) throw new Error("Match calculation failed.");

            currentAnalysis = await matchRes.json();
            checkedSkills.clear(); // Reset checklist
            
            renderAnalysis(currentAnalysis);

        } catch (err) {
            matchPlaceholder.classList.remove("hidden");
            alert(`Matching Error: ${err.message}`);
        } finally {
            matchingStatus.classList.add("hidden");
        }
    }

    function renderUnenrichedJob(job) {
        // Job Header Details
        jobDetailTitle.textContent = job.title;
        jobDetailCompany.textContent = `${job.company} • ${job.location || 'Remote'}`;
        jobDetailSource.textContent = job.source;

        // Reset Readiness Circle to 0%
        updateScoreCircle(0);
        projectedBadge.classList.add("hidden");

        // Reset Breakdown
        scoreSemantic.textContent = "0%";
        fillSemantic.style.width = "0%";
        scoreSkills.textContent = "0%";
        fillSkills.style.width = "0%";
        scoreExperience.textContent = "0%";
        fillExperience.style.width = "0%";
        expExplanation.textContent = "Requirements not yet analyzed.";

        // Clear Overlapping Skills
        overlappingSkillsList.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-muted);">Requirements not yet analyzed. Click below to extract.</span>`;

        // Clear and render manually triggerable gaps card
        gapsList.innerHTML = `
            <div class="card" style="background: rgba(255, 255, 255, 0.02); border-color: var(--border-color); text-align: center; padding: 2rem;">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--text-muted); opacity: 0.5; margin-bottom: 1rem; display: block; margin-left: auto; margin-right: auto;">
                    <path d="M12 16V8M12 8L9 11M12 8L15 11" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <p style="font-size: 0.95rem; margin-bottom: 0.5rem; font-weight: 500;">No skills have been extracted for this job posting yet.</p>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1.25rem;">Our AI Recruiter needs to parse the job description to identify requirements and compute your readiness score.</p>
                <button id="manual-enrich-btn" class="course-btn" style="background: linear-gradient(135deg, var(--primary) 0%, #4a00e0 100%); color: #fff; border: none; padding: 0.75rem 1.5rem; font-size: 0.9rem; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%; box-shadow: 0 0 15px var(--primary-glow); display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: opacity 0.2s;">
                    <span>Analyze Requirements with AI Recruiter</span>
                </button>
            </div>
        `;

        // Add event listener to the manual enrich button
        const enrichBtn = document.getElementById("manual-enrich-btn");
        enrichBtn.addEventListener("click", async () => {
            enrichBtn.disabled = true;
            enrichBtn.style.opacity = "0.7";
            enrichBtn.innerHTML = `<div class="spinner" style="width: 16px; height: 16px; border-width: 1.5px;"></div> <span>AI Recruiter parsing description...</span>`;

            try {
                const enrichRes = await fetch(`${API_URL}/api/jobs/enrich`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(job)
                });

                if (!enrichRes.ok) {
                    const errData = await enrichRes.json();
                    throw new Error(errData.detail || "Rate limit reached. Please wait a minute and try again.");
                }

                const enrichedJob = await enrichRes.json();
                
                // Update the job list arrays so we don't have to fetch it again on next click
                const selectedIdx = document.querySelector(".job-item.selected").dataset.index;
                jobListings[selectedIdx] = enrichedJob;
                selectedJob = enrichedJob;

                // Re-run calculate gap with enriched job
                calculateGap(enrichedJob);

            } catch (err) {
                alert(`AI Recruiter Error: ${err.message}`);
                // Restore button state
                enrichBtn.disabled = false;
                enrichBtn.style.opacity = "1";
                enrichBtn.innerHTML = `<span>Analyze Requirements with AI Recruiter</span>`;
            }
        });

        // Reset Roadmap
        roadmapList.innerHTML = `
            <div class="timeline-item">
                <div class="timeline-dot" style="background: var(--text-muted); box-shadow: none;"></div>
                <div class="timeline-content">
                    <div class="timeline-title">Roadmap Pending</div>
                    <div class="timeline-desc">A personalized timeline will be generated once requirements are analyzed.</div>
                </div>
            </div>
        `;

        matchReport.classList.remove("hidden");
    }

    function renderAnalysis(analysis) {
        // Job Header Details
        jobDetailTitle.textContent = analysis.job_title;
        jobDetailCompany.textContent = `${analysis.company} • ${selectedJob.location || 'Remote'}`;
        jobDetailSource.textContent = selectedJob.source;

        // Render current score
        updateScoreCircle(analysis.current_readiness);

        // Render Breakdown details
        const b = analysis.readiness_breakdown;
        scoreSemantic.textContent = `${b.semantic_similarity.score}%`;
        fillSemantic.style.width = `${b.semantic_similarity.score}%`;

        scoreSkills.textContent = `${b.skill_matching.score}%`;
        fillSkills.style.width = `${b.skill_matching.score}%`;

        scoreExperience.textContent = `${b.experience_matching.score}%`;
        fillExperience.style.width = `${b.experience_matching.score}%`;
        
        expExplanation.textContent = `${b.experience_matching.candidate_years} yrs verified experience vs ${b.experience_matching.expected_years} yrs expected for ${selectedJob.seniority || 'Mid'}`;

        // Render Overlapping Skills
        overlappingSkillsList.innerHTML = "";
        const matchedSkills = b.skill_matching.matched || [];
        if (matchedSkills.length === 0) {
            overlappingSkillsList.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-muted);">No overlapping skills found yet.</span>`;
        } else {
            matchedSkills.forEach(skill => {
                const badge = document.createElement("span");
                badge.className = "skill-badge";
                badge.innerHTML = `
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    ${skill.toUpperCase()}
                `;
                overlappingSkillsList.appendChild(badge);
            });
        }

        // Render Gap checklist
        renderGaps(analysis.recommendations);
        
        // Render learning roadmap
        renderRoadmap(analysis.recommendations);

        matchReport.classList.remove("hidden");
    }

    function updateScoreCircle(score) {
        // Round score
        const rounded = Math.round(score);
        readinessScoreNum.textContent = `${rounded}%`;

        // Calculate SVG circle dashoffset
        // 0% -> offset = 377
        // 100% -> offset = 0
        const offset = CIRCLE_CIRCUMFERENCE - (CIRCLE_CIRCUMFERENCE * rounded) / 100;
        progressBar.style.strokeDashoffset = offset;
    }

    function renderGaps(recommendations) {
        gapsList.innerHTML = "";
        
        if (recommendations.length === 0) {
            gapsList.innerHTML = `
                <div class="status-box" style="background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.2);">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--success)">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke-linecap="round"/>
                        <path d="M22 4L12 14.01l-3-3" stroke-linecap="round"/>
                    </svg>
                    <span style="color: var(--success); font-weight: 600;">Perfect Match! You meet all skills listed in this job requirement.</span>
                </div>
            `;
            return;
        }

        recommendations.forEach(rec => {
            const card = document.createElement("div");
            card.className = "gap-item-card";

            // Render Course Recommendations
            let coursesHtml = "";
            if (rec.courses && rec.courses.length > 0) {
                coursesHtml = `<div class="courses-list">`;
                rec.courses.forEach(c => {
                    const typeLabel = c.course.type || (c.course.free ? "Free Tutorial" : "Certificate Course");
                    coursesHtml += `
                        <div class="course-card">
                            <div class="course-info">
                                <h5>${c.course.title}</h5>
                                <span>${c.course.provider} • <strong>${typeLabel}</strong> • Duration: ${c.course.duration}</span>
                            </div>
                            <div class="course-meta">
                                <span class="course-confidence">${Math.round(c.confidence)}% Confidence</span>
                                <a href="${c.course.link}" target="_blank" class="course-btn">Start</a>
                            </div>
                        </div>
                    `;
                });
                coursesHtml += `</div>`;
            } else {
                coursesHtml = `
                    <div class="courses-list">
                        <div class="course-card" style="border-style: dashed; justify-content: center;">
                            <span style="font-size: 0.75rem; color: var(--text-muted);">No catalog courses. Let CourseAgent search the web.</span>
                        </div>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="gap-row" data-skill="${rec.skill}">
                    <label class="checkbox-container">
                        <input type="checkbox" class="skill-checkbox">
                        <span class="checkmark"></span>
                    </label>
                    <span class="gap-skill-name">${rec.skill.toUpperCase()}</span>
                    <span class="gap-skill-demand">${Math.round(rec.market_demand_frequency)}% demand</span>
                    <span class="gap-improvement-tag">+${rec.projected_improvement}% readiness</span>
                </div>
                ${coursesHtml}
            `;

            // Toggle Handler for projected readiness
            const checkbox = card.querySelector(".skill-checkbox");
            checkbox.addEventListener("change", (e) => {
                if (e.target.checked) {
                    checkedSkills.add(rec.skill.toLowerCase());
                } else {
                    checkedSkills.delete(rec.skill.toLowerCase());
                }
                recalculateProjectedScore();
            });

            gapsList.appendChild(card);
        });
    }

    function renderRoadmap(recommendations) {
        roadmapList.innerHTML = "";
        
        if (recommendations.length === 0) {
            roadmapList.innerHTML = `
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                        <div class="timeline-title">Ready to Apply!</div>
                        <div class="timeline-desc">No skill gaps detected. Go ahead and apply for this job posting.</div>
                    </div>
                </div>
            `;
            return;
        }

        recommendations.forEach((rec, idx) => {
            const item = document.createElement("div");
            item.className = "timeline-item";

            // Find best course
            const bestCourse = rec.courses && rec.courses.length > 0 ? rec.courses[0].course : null;
            const courseTitle = bestCourse ? `"${bestCourse.title}" via ${bestCourse.provider}` : "self-paced documentation";
            const duration = bestCourse ? bestCourse.duration : "1 week";

            item.innerHTML = `
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-title">Milestone ${idx + 1}: Acquire ${rec.skill.toUpperCase()}</div>
                    <div class="timeline-desc">Study ${courseTitle}. Expected completion: ${duration}.</div>
                </div>
            `;
            roadmapList.appendChild(item);
        });
    }

    // Client-side real-time projected calculations
    function recalculateProjectedScore() {
        if (!currentAnalysis) return;

        const b = currentAnalysis.readiness_breakdown;
        
        // 1. Get original values
        const semanticScore = b.semantic_similarity.score;
        const expScore = b.experience_matching.score;
        const originalMatched = b.skill_matching.matched.map(s => s.toLowerCase());
        const originalMissing = b.skill_matching.missing.map(s => s.toLowerCase());
        
        // 2. Compute new matched list
        const simulatedMatched = [...originalMatched];
        originalMissing.forEach(skill => {
            if (checkedSkills.has(skill)) {
                simulatedMatched.push(skill);
            }
        });

        // 3. Compute skill matching score
        const totalSkillsNum = originalMatched.length + originalMissing.length;
        const newSkillScore = totalSkillsNum > 0 ? (simulatedMatched.length / totalSkillsNum) * 100 : 100;

        // 4. Compute composite
        const newProjectedScore = 0.50 * semanticScore + 0.35 * newSkillScore + 0.15 * expScore;

        // Render updates
        if (checkedSkills.size > 0) {
            projectedBadge.classList.remove("hidden");
            projectedScoreNum.textContent = `${Math.round(newProjectedScore)}%`;
            updateScoreCircle(newProjectedScore);
            
            // Highlight skill bar
            scoreSkills.textContent = `${Math.round(newSkillScore)}%`;
            fillSkills.style.width = `${newSkillScore}%`;
            scoreSkills.style.color = "var(--accent)";
        } else {
            projectedBadge.classList.add("hidden");
            updateScoreCircle(currentAnalysis.current_readiness);
            
            // Revert skill bar
            scoreSkills.textContent = `${b.skill_matching.score}%`;
            fillSkills.style.width = `${b.skill_matching.score}%`;
            scoreSkills.style.color = "var(--text-main)";
        }
    }
});
