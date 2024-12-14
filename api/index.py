from flask import Flask, request, jsonify, send_file, render_template
import os
import requests
import json
import re
import tempfile
import pprint
app = Flask(__name__)

# Set your Gemini API key here dsds
GEMINI_API_KEY = 'AIzaSyDO7Lel7_O8J616TI9zcccOmZ1DXC0ZdKo'  # Replace with your actual API key

def validate_latex(latex_code):
    # Simple validation to check if basic LaTeX structure exists
    return '\\begin{document}' in latex_code and '\\end{document}' in latex_code

def remove_comments(latex_code):
    # Removes any lines starting with % (LaTeX comments)
    return re.sub(r'(?<!\\)%.*', '', latex_code)

def extract_section(latex_code, section_name):
    # First, remove comments from the LaTeX code
    cleaned_latex_code = remove_comments(latex_code)
    
    # Escape the section name to handle special characters
    section_name_escaped = re.escape(section_name)
    
    # Regular expression to extract a specific section
    pattern = rf'\\section\{{{section_name_escaped}\}}(.*?)(?=\\section|\\end\{{document\}})'
    
    # Search for the pattern in the cleaned LaTeX code
    match = re.search(pattern, cleaned_latex_code, re.DOTALL)
    
    if match:
        return match.group(1).strip()  # Return the content of the section without extra spaces
    
    return f"Error: {section_name} section not found."


def tailor_section(api_key, section, job_description):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'
    print(f"section is {section}")
    if not section.strip():
        return "Error: The provided section is empty."
    if section=="Skills":
        print("Inside the skill section-----------------------------------------------------------------------------------------------------")
        prompt = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Tailor the {section} section to fit the job description: {job_description}. \nSection: {section} ensure all keywords are included in {section}  from the  {job_description} ,all keywords in {job_description}  should be included in {section} check it  and return only the latex code."
                        }
                    ]
                }
            ]
        }
    else:
         prompt = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Revise and tailor the '{section}' section to align closely with the provided job description: '{job_description}'. Ensure that all relevant keywords and phrases from the job description are incorporated seamlessly into the '{section}' content. Focus solely on integrating these keywords naturally and appropriately. Return only the final, tailored LaTeX code for the '{section}', and make no other changes or additions."
                        }
                    ]
                }
            ]
        }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(prompt))

        if response.status_code == 200:
            response_json = response.json()
            print("Full API Response:", json.dumps(response_json, indent=2))

            if 'candidates' in response_json and len(response_json['candidates']) > 0:
                content = response_json['candidates'][0].get('content', {}).get('parts', [])
                
                if content and isinstance(content[0], dict):
                    latex_code = content[0].get('text', "")
                    
                    if latex_code:
                        # Return the latex code directly without regex if it's already structured.
                        return latex_code.strip()
                    else:
                        return "Error: No LaTeX code found in content."
                else:
                    return "Error: Invalid content format in response."
            else:
                return "Error: No candidates found in API response."
        else:
            return f"Error: Unable to contact API. Status code: {response.status_code}, Message: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Error: API request failed. Exception: {str(e)}"



@app.route('/upload', methods=['POST'])
def upload():
    resume_file = request.files['resume']
    job_description = request.form['job_description']
    
    latex_code = resume_file.read().decode('utf-8')
    # if not validate_latex(latex_code):
    #     return jsonify({"error": "Invalid LaTeX code."}), 400

    # Extract sections from LaTeX
    work_experience_section = extract_section(latex_code, "Work Experience")
    print("-------------------------")
    projects_section = extract_section(latex_code, "Project Work")

    achievements_section = extract_section(latex_code, "Achievements")
    skills_section=extract_section(latex_code,"Skills")
    # Check if sections are empty and provide feedback
    if "Error" in work_experience_section:
        return jsonify({"error": "Work Experience section not found in LaTeX."}), 400
    if "Error" in projects_section:
        return jsonify({"error": "Project Work section not found in LaTeX."}), 400
    if "Error" in achievements_section:
        return jsonify({"error": "Achievements section not found in LaTeX."}), 400

    # Tailor each section based on the job description
    tailored_experience = tailor_section(GEMINI_API_KEY, work_experience_section, job_description)
    tailored_projects = tailor_section(GEMINI_API_KEY, projects_section, job_description)
    tailored_achievements = tailor_section(GEMINI_API_KEY, achievements_section, job_description)
    tailored_skills= tailor_section(GEMINI_API_KEY, skills_section, job_description)
    print("The exp is::",tailored_experience)
    print("----------------------------------------")
    # Create the final LaTeX document
    final_latex = f"""
        \\documentclass[a4paper,10pt]{{article}}

        %----------------------------------------------------------------------------------------
        %	FONT
        %----------------------------------------------------------------------------------------

        % % fontspec allows you to use TTF/OTF fonts directly
        % \\usepackage{{fontspec}}
        % \\defaultfontfeatures{{Ligatures=TeX}}

        % % modified for ShareLaTeX use
        % \\setmainfont[
        % SmallCapsFont = Fontin-SmallCaps.otf,
        % BoldFont = Fontin-Bold.otf,
        % ItalicFont = Fontin-Italic.otf
        % ]
        % {{Fontin.otf}}

        %----------------------------------------------------------------------------------------
        %	PACKAGES
        %----------------------------------------------------------------------------------------
        \\usepackage{{url}}
        \\usepackage{{parskip}}

        %other packages for formatting
        \\RequirePackage{{color}}
        \\RequirePackage{{graphicx}}
        \\usepackage[usenames,dvipsnames]{{xcolor}}
        \\usepackage[scale=0.9, top=.1in, bottom=.1in]{{geometry}}

        %tabularx environment
        \\usepackage{{tabularx}}

        %for lists within experience section
        \\usepackage{{enumitem}}

        % centered version of 'X' col. type
        \\newcolumntype{{C}}{{>{{\\centering\\arraybackslash}}X}}

        %to prevent spillover of tabular into next pages
        \\usepackage{{supertabular}}
        \\usepackage{{tabularx}}
        \\newlength{{\\fullcollw}}
        \\setlength{{\\fullcollw}}{{0.47\\textwidth}}

        %custom \\section
        \\usepackage{{titlesec}}
        \\usepackage{{multicol}}
        \\usepackage{{multirow}}

        %CV Sections inspired by:
        %http://stefano.italians.nl/archives/26
        \\titleformat{{\\section}}{{\\Large\\scshape\\raggedright}}{{}}{{0em}}{{}}[\\titlerule]
        \\titlespacing{{\\section}}{{0pt}}{{5.25pt}}{{5.25pt}}

        %for publications
        \\usepackage[style=authoryear,sorting=ynt, maxbibnames=2]{{biblatex}}

        %Setup hyperref package, and colours for links
        \\usepackage[unicode, draft=false]{{hyperref}}
        \\definecolor{{linkcolour}}{{rgb}}{{0,0.2,0.6}}
        \\hypersetup{{colorlinks,breaklinks,urlcolor=linkcolour,linkcolor=linkcolour}}
        \\addbibresource{{citations.bib}}
        \\setlength\\bibitemsep{{1em}}

        %for social icons
        \\usepackage{{fontawesome5}}

        %debug page outer frames
        %\\usepackage{{showframe}}

        %----------------------------------------------------------------------------------------
        %	BEGIN DOCUMENT
        %----------------------------------------------------------------------------------------
        \\begin{{document}}

        % non-numbered pages
        \\pagestyle{{empty}}

        %----------------------------------------------------------------------------------------
        %	TITLE
        %----------------------------------------------------------------------------------------

        \\begin{{tabularx}}{{\\linewidth}}{{@{{}} C @{{}}}}\\\\
        \\Huge{{Yash Shah}} \\\\[2pt]
        \\href{{https://github.com/yash161}}{{\\raisebox{{-0.05\\height}}\\faGithub\\ yash161}} \\ $|$
        \\href{{https://www.linkedin.com/in/yash-shah-b7129b1bb/}}{{\\raisebox{{-0.05\\height}}\\faLinkedin\\ yash-shah}} \\ $|$ \\ 
        \\href{{mailto:yashshah3698@gmail.com}}{{\\raisebox{{-0.05\\height}}\\faEnvelope \\ yashshah3698@gmail.com}} \\ $|$ \\ 
        \\href{{tel:+12133018249}}{{\\raisebox{{-0.05\\height}}\\faMobile \\ 2133018249 (Open to Relocate)}} \\\\
        \\end{{tabularx}}

        %----------------------------------------------------------------------------------------
        % EXPERIENCE SECTIONS
        %----------------------------------------------------------------------------------------
        \\section{{Education}}
        \\begin{{tabularx}}{{\\linewidth}}{{ @{{}}l r@{{}} }}
        \\color[HTML]{{1C033C}} \\textbf{{California State University, Los Angeles, United States}} & \\hfill \\color[HTML]{{371e77}} August 2024 - August 2026 \\\\
        \\color[HTML]{{371e77}} M.S. in Computer Science & \\hfill \\color[HTML]{{4B28A4}}  \\\\
        \\multicolumn{{2}}{{@{{}}X@{{}}}}{{Relevant Coursework: Advanced AI, Advanced Software Engineering, Computer and Network Security}}
        \\end{{tabularx}}
        \\setlength{{\\parskip}}{{2pt}}
        \\begin{{tabularx}}{{\\linewidth}}{{ @{{}}l r@{{}} }}
        \\color[HTML]{{1C033C}} \\textbf{{Ganpat University, Gujarat, India}} & \\hfill \\color[HTML]{{371e77}} July 2019 - June 2023 \\\\
        \\color[HTML]{{371e77}} B.Tech. in Computer Science \\& Engineering (Cloud-Based Applications) & \\hfill \\color[HTML]{{4B28A4}} \\textit{{\\textbf{{CGPA: 8.99/10}}}} \\\\
        \\multicolumn{{2}}{{@{{}}X@{{}}}}{{Relevant Coursework: Cloud Computing, Machine Learning, Cloud Security, Data Mining \\& Warehousing, Software Engineering, Computer Networks, Algorithm Design, Microservices, Virtualization, Operating Systems, DBMS, Data Structures, Compiler Design, IT Infrastructure Management, Web App Development}}
        \\end{{tabularx}}
        \\vspace{{-3mm}}

        \\section{{Work Experience}}
        {tailored_experience}

        \\vspace{{-5mm}}
        \\section{{Project Work}}
        {tailored_projects}

        \\vspace{{-1mm}}
        \\section{{Skills}}
        {tailored_skills}
        \\vspace{{-4mm}}

        %----------------------------------------------------------------------------------------
        %	PUBLICATIONS
        %----------------------------------------------------------------------------------------
        \\section{{Achievements}}
        {tailored_achievements}

        \\end{{document}}
"""

    
    # Use a temporary file to save the final LaTeX document
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tex', mode='w', encoding='utf-8')
    latex_filename = temp_file.name
    with open(latex_filename, 'w', encoding='utf-8') as f:
        f.write(final_latex)

    # Send the file for download
    return send_file(latex_filename, as_attachment=True, download_name='final_resume.tex')



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
