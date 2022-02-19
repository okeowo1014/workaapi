import secrets
import string
from string import punctuation

import en_core_web_sm

nlp = en_core_web_sm.load()
custom_tag = ['design', 'operations', 'technical', 'training', 'sales', 'marketing', 'reporting', 'compliance',
              'strategy',
              'research', 'analytical', 'engineering', 'policies', 'budget', 'finance', 'project management', 'health',
              'customer service', 'documentation', 'content', 'presentation', 'brand', 'presentations', 'safety',
              'certification', 'accounting', 'regulations', 'metrics', 'legal', 'engagement', 'database', 'analytics',
              'distribution', 'coaching', 'testing', 'vendors', 'consulting', 'writing', 'contracts', 'inventory',
              'retail',
              'healthcare', 'regulatory', 'scheduling', 'construction', 'logistics', 'mobile',
              'C (programming language)',
              'programming language', 'programming', 'correspondence', 'controls', 'human resources', 'specifications',
              'recruitment', 'procurement', 'partnership', 'partnerships', 'management experience', 'negotiation',
              'hardware',
              'programming', 'agile', 'forecasting', 'advertising', 'business development', 'audit', 'architecture',
              'supply chain', 'governance', 'staffing', 'continuous improvement', 'product development', 'networking',
              'recruiting', 'product management', 'CRM', 'SAP', 'troubleshooting', 'computer science', 'budgeting',
              'electrical', 'customer experience', 'I-DEAS', 'economics', 'information technology', 'transportation',
              'social media', 'automation', 'lifecycle', 'filing', 'modeling', 'investigation', 'SQL', 'editing',
              'purchasing', 'KPIs', 'hospital', 'forecasts', 'acquisition', 'expenses', 'billing', 'change management',
              'video', 'invoices', 'administrative support', 'payments', 'lean', 'process improvement', 'installation',
              'risk management', 'transactions', 'investigations', 'payroll', 'R (programming language)',
              'data analysis',
              'statistics', 'coding', 'protocols', 'program management', 'quality assurance', 'windows', 'banking',
              'outreach', 'sourcing', 'Microsoft Office', 'merchandising', 'business requirements', 'drawings',
              'Salesforce',
              'documenting', 'information systems', 'nursing', 'business administration', 'consumers',
              'financial services',
              'legislation', 'strategic planning', 'MS Office', 'counseling', 'technical support', 'frameworks',
              'performance management', 'BI', 'fashion', 'HTML', 'publications', 'internship', 'QA',
              'software development',
              'oracle', 'Java', 'teaching', 'pharmaceutical', 'ERP', 'fulfillment', 'positioning', 'tax',
              'service delivery',
              'investigate', 'editorial', 'account management', 'business process', 'valid drivers license',
              'electronics',
              'PR', 'public relations', 'Javascript', 'assembly', 'digital marketing', 'Linux', 'Facebook',
              'spreadsheets',
              'recruit', 'proposal', 'SharePoint', 'data entry', 'hotel', 'ordering', 'branding', 'life cycle',
              'real estate',
              'relationship management', 'researching', 'process improvements', 'chemistry', 'SaaS', 'CAD',
              'sales experience', 'mathematics', 'customer-facing', 'audio', 'project management skills', 'six sigma',
              'hospitality', 'mechanical engineering', 'auditing', 'employee relations', 'android',
              'security clearance',
              'licensing', 'Adobe', 'fundraising', 'repairs', 'ISO', 'market research', 'warehouse',
              'business strategy',
              'PMP', 'data management', 'quality control', 'reconciliation', 'CSS', 'conversion', 'business analysis',
              'financial analysis', 'ecommerce', 'business intelligence', 'C++', 'client service', 'publishing',
              'supervising', 'complex projects', 'key performance indicators', 'scrum', 'Photoshop', 'sports',
              'e-commerce',
              'journalism', 'D (programming language)', 'data collection', 'higher education', 'marketing programs',
              'financial management', 'business plans', 'user experience', 'client relationships', 'cloud',
              'analytical skills', 'Cisco', 'internal stakeholders', 'product marketing', 'regulatory requirements',
              'ITIL',
              'information security', 'aviation', 'supply chain management', 'Python', 'accounts payable',
              'industry experience', 'AutoCAD', 'purchase orders', 'acquisitions', 'TV', 'instrumentation',
              'strategic direction', 'law enforcement', 'call center', 'experiments', 'technical skills',
              'human resource',
              'business cases', 'build relationships', 'invoicing', 'support services', 'marketing strategy',
              'operating systems', 'biology', 'start-up', 'electrical engineering', 'workflows', 'routing',
              'non-profit',
              'marketing plans', 'due diligence', 'business management', 'iPhone', 'algorithms', 'architectures',
              'reconcile',
              'dynamic environment', 'external partners', 'asset management', 'Microsoft Word', 'EMEA', 'intranet',
              'SOPs',
              'SAS', 'digital media', 'prospecting', 'financial reporting', 'project delivery', 'SEO',
              'operational excellence', 'standard operating procedures', 'C#', 'technical knowledge', 'on-call',
              'talent management', 'stakeholder management', 'tablets', 'CMS', 'analyze data', 'financial statements',
              'Microsoft Office Suite', 'fitness', 'case management', 'value proposition', 'industry trends', 'RFP',
              'broadcast', 'portfolio management', 'fabrication', 'UX', 'financial performance',
              'customer requirements',
              'psychology', 'marketing materials', 'resource management', 'physics', 'mortgage',
              'development activities',
              'end user', 'business planning', 'root cause', 'analysis', 'leadership development',
              'relationship building',
              'SDLC', 'on-boarding', 'quality standards', 'regulatory compliance', 'AWS', 'KPI', 'status reports',
              'product line', 'drafting', 'JIRA', 'phone calls', 'product knowledge', 'business stakeholders',
              'technical issues', 'admissions', 'supervisory experience', 'usability', 'pharmacy', 'commissioning',
              'project plan', 'MS Excel', 'FDA', 'test plans', 'variances', 'UI', 'financing', 'travel arrangements',
              'internal customers', 'medical device', 'counsel', 'inventory management', 'performance metrics',
              'lighting',
              'outsourcing', 'InDesign', 'performance improvement', 'management consulting', 'graphic design',
              'transport',
              'information management', '.NET', 'startup', 'matrix', 'front-end', 'project planning',
              'business systems',
              'accounts receivable', 'public health', 'HRIS', 'German', 'instructional design', 'in-store',
              'data center',
              'MATLAB', 'employee engagement', 'cost effective', 'sales management', 'API', 'Adobe Creative Suite',
              'Twitter',
              'program development', 'event planning', 'cash flow', 'strategic plans', 'root cause',
              'vendor management',
              'trade shows', 'hotels', 'segmentation', 'contract management', 'GIS', 'talent acquisition',
              'photography',
              'internal communications', 'client services', 'IBM', 'financial reports', 'product quality', 'beverage',
              'strong analytical skills', 'underwriting', 'CPR', 'mining', 'sales goals', 'chemicals', 'deposits',
              'scripting', 'migration', 'software engineering', 'MIS', 'therapeutic', 'general ledger', 'Tableau',
              'MS Project', 'standardization', 'retention', 'spelling', 'media relations', 'OS', 'daily operations',
              'immigration', 'product design', 'ETL', 'field sales', 'driving record', 'PeopleSoft', 'benchmark',
              'quality management', 'APIs', 'test cases', 'internal controls', 'telecom', 'business issues',
              'research projects', 'data quality', 'strategic initiatives', 'office software', 'CFA', 'co-op',
              'big data',
              'journal entries', 'VMware', 'help desk', 'statistical analysis', 'datasets', 'alliances', 'SolidWorks',
              'prototype', 'LAN', 'SCI', 'budget management', 'Unix', 'RFPs', 'Flex', 'GAAP', 'experimental', 'CPG',
              'information system', 'customer facing', 'process development', 'web services', 'international', 'travel',
              'revenue growth', 'software development life cycle', 'operations management', 'computer applications',
              'risk assessments', 'sales operations', 'raw materials', 'internal audit', 'physical security',
              'SQL server',
              'affiliate', 'computer software', 'manage projects', 'business continuity', 'litigation',
              'IT infrastructure',
              'cost reduction', 'small business', 'annual budget', 'iOS', 'HTML5', 'real-time', 'consulting experience',
              'circuits', 'machine learning', 'risk assessment', 'DNS', 'cross-functional team', 'public policy',
              'analyzing data', 'consulting services']


def extract_keywords(nlp=nlp, sequence=None, special_tags: list = custom_tag):
    """ Takes a Spacy core language model,
    string sequence of text and optional
    list of special tags as arguments.

    If any of the words in the string are
    in the list of special tags they are immediately
    added to the result.

    Arguments:
        sequence {str} -- string sequence to have keywords extracted from

    Keyword Arguments:
        tags {list} --  list of tags to be automatically added (default: {None})

    Returns:
        {list} -- list of the unique keywords extracted from a string
    """
    result = []

    # custom list of part of speech tags we are interested in
    # we are interested in proper nouns, nouns, and adjectives
    # edit this list of POS tags according to your needs.
    pos_tag = ['NOUN']

    # create a spacy doc object by calling the nlp object on the input sequence
    doc = nlp(sequence.lower())

    # if special tags are given and exist in the input sequence
    # add them to results by default
    if special_tags:
        tags = [tag.lower() for tag in special_tags]
        for token in doc:
            if token.text in tags:
                result.append(token.text)

    for chunk in doc.noun_chunks:
        final_chunk = ""
        for token in chunk:
            if token.pos_ in pos_tag:
                final_chunk = final_chunk + token.text + " "
        if final_chunk:
            result.append(final_chunk.strip())

    for token in doc:
        if token.text in nlp.Defaults.stop_words or token.text in punctuation:
            continue
        if token.pos_ in pos_tag:
            result.append(token.text)
    return list(set(result))


text3 = 'A retail salesperson assists customers in making purchases, including processing payments. This type of ' \
        'position exists in a wide variety of businesses that sell merchandise directly to customers, ' \
        'such as furniture, clothing, cars and equipment. Creating a strong job description is essential to defining ' \
        'the responsibilities of this role within your organization and determining the requirements for a ' \
        'candidate.The required skills and experience for a retail salesperson can vary. Some common abilities for ' \
        'which businesses look include verbal communication and customer service skills. It is common for a worker in ' \
        'this position to not need any specific education but instead receive on-the-job training. Job description ' \
        'examples provide insight into what to list in your own posting. '


def generate_job_key():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(16))


def generate_employee_key():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(12))


def generate_employer_key():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))


def generate_interview_key():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))


def generate_obj_question_key():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(7))


def generate_theory_question_key():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(9))


def generate_chat_key():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(16))
