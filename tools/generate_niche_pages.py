#!/usr/bin/env python3
"""
Generates all industry (niche) pages for the website from tools/categories.json.

  python3 tools/generate_niche_pages.py

Creates:
  - industries.html                 (index of every industry)
  - seo-for-<category>.html         (one hub page per category)
  - seo-for-<niche>.html            (one page per subcategory)
and refreshes the industries list inside assets/js/main.js (header + footer).

To add a niche: add its name to tools/categories.json and run this script again.
To change the wording of every niche page: edit the templates below.
"""
import hashlib
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")

# --------------------------------------------------------------------------
# Category level data. Keys are matched by category number in categories.json.
# --------------------------------------------------------------------------
CAT = {
    1: dict(slug="travel-tourism", short="Travel & Tourism", type="local",
            buyers="travellers",
            why="Travel decisions start with research. People compare destinations, prices and reviews on Google weeks before they book, so the businesses visible at every stage of that journey win the enquiry.",
            challenges=["Seasonal demand swings that need content planned months ahead",
                        "Competition from large booking platforms and aggregators",
                        "Trust signals such as reviews, licences and secure payment information",
                        "Destination, itinerary and package pages that are thin or duplicated"],
            note="UK travel businesses often need ATOL or ABTA credentials, and some US states regulate sellers of travel. Show your registration details clearly because it builds trust and supports conversions."),
    2: dict(slug="healthcare-medical", short="Healthcare & Medical", type="local",
            buyers="patients",
            why="People search for a clinic when they have a health concern or a planned treatment, and they usually choose from the first few providers they trust.",
            challenges=["Strict rules on advertising and medical claims",
                        "Patient privacy when using forms, call tracking and analytics",
                        "Treatment pages that must be accurate and reviewed by qualified clinicians",
                        "Intense competition for local map results"],
            note="In the UK, healthcare advertising follows ASA and CAP rules and some providers need CQC registration. In the USA, HIPAA and state rules can affect tracking and patient forms. Always have claims reviewed by a qualified professional."),
    3: dict(slug="legal-services", short="Legal Services", type="local",
            buyers="clients",
            why="Legal problems are urgent and high value. People search by practice area and location, and the firms at the top of the results receive the calls.",
            challenges=["High paid-search costs that make organic rankings more valuable",
                        "Practice area and location pages that need real depth",
                        "Reviews, credentials and trust signals",
                        "Regulated advertising rules that limit what you can say"],
            note="UK solicitors follow SRA transparency and advertising rules, and US lawyers follow state bar advertising rules. We keep copy factual and compliant."),
    4: dict(slug="finance-insurance", short="Finance & Insurance", type="local",
            buyers="customers",
            why="Money decisions carry risk, so people research heavily before they contact a provider. Clear, trustworthy content and strong rankings help you appear at the moment of research.",
            challenges=["Extra scrutiny from Google on financial advice content, so expertise and trust signals matter",
                        "Comparison sites and aggregators dominating results",
                        "Complex products that need clear educational content",
                        "Compliance review cycles that slow publishing"],
            note="UK financial promotions can fall under FCA rules. In the USA, rules from regulators such as the SEC, FINRA, CFPB and state insurance departments may apply. Content should be accurate, balanced and checked by your compliance team."),
    5: dict(slug="real-estate-property", short="Real Estate & Property", type="local",
            buyers="buyers, sellers, landlords and tenants",
            why="Property searches are intensely local. People look for agents, valuations and listings by neighbourhood, so the agencies that own those local searches earn instructions.",
            challenges=["Hyper-local competition by area, postcode and ZIP code",
                        "Large portals such as Rightmove, Zoopla, Zillow and Realtor.com",
                        "Listing pages that change quickly and can create duplicate content",
                        "Thin neighbourhood and market content"],
            note="Show licence numbers and redress scheme or regulator details where required in your market."),
    6: dict(slug="construction-home-improvement", short="Construction & Home Improvement", type="local",
            buyers="homeowners and property managers",
            why="Home projects and repairs are often urgent. People search on their phones, compare a few local companies and call the one that looks most trustworthy.",
            challenges=["Emergency searches that need fast mobile pages and click-to-call",
                        "Separate pages needed for every service and every town served",
                        "Seasonal demand",
                        "Proof of quality: project galleries, reviews and accreditations"],
            note="Display trade accreditations, insurance and licences, such as Gas Safe or NICEIC in the UK, and state or local contractor licences in the USA."),
    7: dict(slug="automotive", short="Automotive", type="local",
            buyers="drivers and car buyers",
            why="Drivers search for sales, servicing and repairs close to home, and they trust reviews. Appearing in local results turns those searches into bookings and showroom visits.",
            challenges=["Marketplace competition from sites such as Autotrader and CarGurus",
                        "Inventory pages that expire and need careful handling",
                        "Urgent repair and breakdown searches",
                        "Review volume and response quality"],
            note=None),
    8: dict(slug="education-training", short="Education & Training", type="local",
            buyers="students and parents",
            why="Choosing a course or school is a long decision. Students and parents research many options online before they request a prospectus or book a visit.",
            challenges=["Long decision cycles that need content for every stage",
                        "Detailed course pages that need clear structure and structured data",
                        "Intake seasons and application deadlines",
                        "International students searching from other countries"],
            note="Make accreditation and regulator information easy to find, because it is a key trust factor for students and parents."),
    9: dict(slug="ecommerce-retail", short="Ecommerce & Retail", type="online",
            buyers="online shoppers",
            why="Shoppers search for products, brands and comparisons before they buy. Organic traffic lowers your reliance on paid ads and brings in buyers at a better margin.",
            challenges=["Thousands of product pages with thin or duplicate content",
                        "Filters and sorting options that create duplicate URLs",
                        "Marketplace competition from Amazon and eBay",
                        "Seasonal peaks such as Black Friday and Christmas"],
            note=None),
    10: dict(slug="hospitality-restaurants", short="Hospitality & Restaurants", type="local",
             buyers="diners and guests",
             why="Diners and guests search for somewhere to eat or stay right now, usually on a phone. Showing up in map results with good photos and reviews decides who gets the booking.",
             challenges=["Map pack competition in busy areas",
                         "Dependence on booking platforms such as OpenTable, Booking.com and Tripadvisor",
                         "Seasonal and weekday demand swings",
                         "Menu, event and venue pages that are image-only and invisible to search engines"],
             note=None),
    11: dict(slug="beauty-personal-care", short="Beauty & Personal Care", type="local",
             buyers="clients",
             why="Beauty clients choose by location, price, reviews and photos. A strong local presence and well-optimised treatment pages bring in regular, repeat bookings.",
             challenges=["Image-heavy websites that load slowly on mobile",
                         "Treatment pages that need unique, helpful content",
                         "Reviews and before-and-after proof",
                         "Easy online booking that is tracked as a conversion"],
             note="Clinics offering aesthetic treatments should keep claims honest and follow advertising rules in their market."),
    12: dict(slug="technology-it", short="Technology & IT", type="online",
             buyers="business buyers",
             why="Business buyers research software and IT providers on Google long before they speak to sales. Content that matches each stage of that research builds pipeline.",
             challenges=["Long B2B sales cycles",
                         "Competitive terms dominated by high-authority websites",
                         "Technical content that must be accurate",
                         "Comparison, alternative and integration searches"],
             note=None),
    13: dict(slug="business-professional-services", short="Business & Professional Services", type="online",
             buyers="business owners and managers",
             why="Companies hire professional service providers on trust and expertise. Ranking for the services and problems they search for puts you on the shortlist.",
             challenges=["Services that look similar, so differentiation matters",
                         "Authority and credibility signals",
                         "Both national and local search targeting",
                         "Long sales cycles that need nurturing content"],
             note=None),
    14: dict(slug="manufacturing-industrial", short="Manufacturing & Industrial", type="b2b",
             buyers="procurement teams and engineers",
             why="Procurement teams and engineers search for suppliers by material, specification and application. Clear product content and strong rankings bring qualified requests for quotes.",
             challenges=["Technical product catalogues and specification data",
                         "Lower search volume that still carries high order value",
                         "Datasheets and PDFs that need to be crawlable",
                         "Targeting export buyers in the UK and USA separately"],
             note=None),
    15: dict(slug="logistics-transportation", short="Logistics & Transportation", type="hybrid",
             buyers="businesses and shippers",
             why="Shippers and businesses compare logistics providers on route, service level and price. Ranking for those searches brings in quote requests from ready-to-ship customers.",
             challenges=["Competition from national carriers and freight marketplaces",
                         "Route, lane and service pages that need unique content",
                         "Quote-request journeys that must be simple and fast",
                         "Trust and compliance information"],
             note=None),
    16: dict(slug="home-personal-services", short="Home & Personal Services", type="local",
             buyers="households",
             why="Households book cleaners, handymen and restoration teams by searching nearby. Appearing in local results with strong reviews wins repeat customers.",
             challenges=["Emergency and same-day searches",
                         "Service-area pages for each town",
                         "Review volume and photos of real work",
                         "Directory sites that rank above individual businesses"],
             note=None),
    17: dict(slug="fitness-sports-wellness", short="Fitness, Sports & Wellness", type="local",
             buyers="members and clients",
             why="People choose a gym, studio or coach close to home or work. Strong local rankings and clear class and pricing pages turn searchers into trial sessions and members.",
             challenges=["Local competition among gyms and studios",
                         "Class timetable and pricing pages that stay up to date",
                         "New Year and seasonal enquiry peaks",
                         "Reviews, photos and trial-offer conversions"],
             note=None),
    18: dict(slug="events-entertainment-media", short="Events, Entertainment & Media", type="hybrid",
             buyers="event organisers and couples",
             why="Event planners, couples and brands search for suppliers by event type and date. Portfolios and reviews that rank well win high-value bookings.",
             challenges=["Portfolio pages that are image-heavy and slow",
                         "Seasonal booking periods such as wedding season",
                         "Directory competition from marketplaces",
                         "Showing real work, not stock photos"],
             note=None),
    19: dict(slug="pet-services", short="Pet Services", type="local",
             buyers="pet owners",
             why="Pet owners look for trusted care close to home and rely heavily on reviews. Local visibility builds a loyal base of repeat customers.",
             challenges=["Trust is the main buying factor, so reviews and credentials matter",
                         "Local competition and directory listings",
                         "Seasonal peaks such as holidays",
                         "Booking and enquiry forms that work well on mobile"],
             note=None),
    20: dict(slug="specialist-niche-services", short="Specialist & Niche Services", type="hybrid",
             buyers="customers",
             why="Specialist services have fewer competitors, but customers still start with a search. Owning the right terms makes you the obvious choice in your niche.",
             challenges=["Lower search volume that needs precise keyword targeting",
                         "Educating customers who do not know the right search terms",
                         "Regional and national targeting",
                         "Regulation and compliance information in some sectors"],
             note=None),
}

KEYWORDS = {
    "local": [("{n} near me", "Local intent"),
              ("best {n} in London", "Local comparison (UK)"),
              ("{n} in New York", "Local intent (USA)"),
              ("affordable {n}", "Price-conscious buyers"),
              ("{n} reviews", "Trust research")],
    "hybrid": [("{n} near me", "Local intent"),
               ("best {n} UK", "Commercial comparison"),
               ("top {n} in the USA", "Commercial comparison"),
               ("{n} cost", "Price research"),
               ("get a quote from {n}", "Ready to enquire")],
    "online": [("best {n} UK", "Commercial comparison"),
               ("top {n} in the USA", "Commercial comparison"),
               ("{n} pricing", "Price research"),
               ("{n} reviews", "Trust research"),
               ("{n} alternatives", "Comparison shopping")],
    "b2b": [("{n} UK", "Supplier search (UK)"),
            ("{n} USA", "Supplier search (USA)"),
            ("best {n}", "Commercial comparison"),
            ("{n} price", "Price research"),
            ("{n} quote", "Ready to enquire")],
}

SERVICES = {
    "local": [
        ("Local SEO", "local-seo-services.html", "Google Business Profile optimisation, citations and reviews that help you appear in the map pack for searches such as “{kw}”."),
        ("Technical SEO", "technical-seo-services.html", "Fast, mobile-friendly pages that search engines can crawl easily, which matters because most local searches happen on phones."),
        ("Service and location pages", "content-marketing-services.html", "Content written around real customer questions in the {nl} sector, with a page for each service and each area you serve."),
        ("Link building", "link-building-services.html", "Relevant local and industry links that build trust with search engines and customers."),
        ("Lead tracking", "contact.html#quote", "Call, WhatsApp and form tracking so you can see exactly which searches produce enquiries."),
        ("Monthly reporting", "about.html", "Clear reports on rankings, traffic and leads, with the next steps for the coming month."),
    ],
    "hybrid": [
        ("Local and national SEO", "local-seo-services.html", "Local visibility for customers nearby and national rankings for wider searches such as “{kw}”."),
        ("Technical SEO", "technical-seo-services.html", "Site speed, crawlability and structured data fixes that remove ranking roadblocks."),
        ("Content marketing", "content-marketing-services.html", "Service pages, guides and case studies that answer the questions customers ask in the {nl} sector."),
        ("Link building", "link-building-services.html", "Editorially earned links from relevant, trusted websites."),
        ("Lead tracking", "contact.html#quote", "Call, WhatsApp and form tracking so every enquiry is attributed to its source."),
        ("Monthly reporting", "about.html", "Plain-English reports on rankings, traffic and leads, with clear next steps."),
    ],
    "online": [
        ("Keyword research and strategy", "content-marketing-services.html", "Research into buying-intent searches such as “{kw}”, mapped to the right page on your website."),
        ("Technical SEO", "technical-seo-services.html", "Speed, crawlability, Core Web Vitals and structured data that help every page perform."),
        ("On-page optimisation", "ecommerce-seo-services.html", "Titles, headings, product and service copy and internal links tuned for the {nl} sector."),
        ("Link building", "link-building-services.html", "Digital PR and outreach that earn authority links from relevant websites."),
        ("Lead and sales tracking", "contact.html#quote", "Track calls, forms and WhatsApp chats so you know which content generates revenue."),
        ("Monthly reporting", "about.html", "Plain-English reports on rankings, traffic and leads, with clear next steps."),
    ],
    "b2b": [
        ("Product and category pages", "content-marketing-services.html", "Clear specification, application and material content that matches how buyers search, such as “{kw}”."),
        ("Technical SEO", "technical-seo-services.html", "Crawlable catalogues, indexable PDFs and structured data so search engines understand your products."),
        ("Lead-generation landing pages", "contact.html#quote", "Quote-request pages built to turn supplier searches into qualified enquiries."),
        ("Link building", "link-building-services.html", "Links from industry directories, trade bodies and relevant publications."),
        ("Export market targeting", "seo-company-usa.html", "Separate keyword and content strategies for UK and US buyers."),
        ("Monthly reporting", "about.html", "Plain-English reports on rankings, traffic and enquiries, with clear next steps."),
    ],
}

# Hand-written extra insight and FAQs for the highest-priority niches.
PRIORITY = {
    "Travel Agencies": dict(
        title="How Travel Agencies Win More Bookings from Search",
        text="Travel agencies win by owning destination and package searches, such as “holiday packages to Dubai” or “safari tour operators”. Build a hub page for each destination with itineraries, best time to visit, visa notes and price guidance, then link each hub to your enquiry form. Cover the whole journey, from inspiration to booking.",
        faqs=[("Which pages matter most on a travel agency website?", "Destination hubs, package and itinerary pages, and clear enquiry forms matter most. Add reviews, registration details and FAQs to build trust."),
              ("Can a small travel agency compete with big booking sites?", "Yes. Focus on specialist destinations, personal service, expert content and local reviews instead of broad terms dominated by large platforms.")]),
    "Airport Transfer Services": dict(
        title="SEO for Airport Transfer Services: Win Route-Based Searches",
        text="Airport transfer searches are route-based, such as “Heathrow to central London taxi” or “JFK to Manhattan car service”. Create a dedicated page for each airport and each popular route, with fixed-price information, vehicle options, flight-tracking details and a simple booking form.",
        faqs=[("Should I create a page for every airport route?", "Create pages for your busiest airports and routes first, each with unique content on journey time, pricing, vehicles and pick-up details. Expand as demand grows."),
              ("Do reviews affect airport transfer rankings?", "Yes. Reviews strongly influence local results and customer trust, so build a steady process for collecting and answering them.")]),
    "Chauffeur Services": dict(
        title="SEO for Chauffeur Services: Rank for Every Occasion",
        text="Chauffeur customers search by occasion and vehicle, for example “wedding car hire”, “corporate chauffeur” or “executive airport transfers”. Build a separate page for each use case with fleet photos, pricing guidance, operator licensing details and an easy enquiry form.",
        faqs=[("Which keywords work best for chauffeur companies?", "Occasion-led and location-led terms such as wedding chauffeur, corporate chauffeur and airport chauffeur in your city usually convert best."),
              ("How can a chauffeur company build trust online?", "Show your fleet, licences, insurance, driver standards and real client reviews on service pages and your Google Business Profile.")]),
    "Roofing Companies": dict(
        title="Roofing SEO: Capture Urgent and Planned Roofing Searches",
        text="Roofing demand is driven by urgency and weather events, with searches like “emergency roof repair” and “roof leak repair near me”. Build pages for repair, replacement, flat roofs and inspections, a page for each town you cover, and project galleries with before-and-after images.",
        faqs=[("Which roofing keywords should I target first?", "Start with emergency repair, roof replacement and your main service area terms, then add flat roof, tiling, shingle and inspection pages."),
              ("How important is a Google Business Profile for roofers?", "It is essential. Most roofing searches show a map pack, so complete profiles with service areas, photos and reviews bring a large share of calls.")]),
    "Plumbing Companies": dict(
        title="Plumber SEO: Be the First Call for Emergency Plumbing Searches",
        text="Plumbing demand is emergency-led, with searches like “emergency plumber near me” and “24 hour plumber”. You need fast mobile pages, click-to-call buttons, a complete Google Business Profile with your service areas, and separate pages for leaks, drains, boilers and bathrooms. UK plumbers doing gas work should show Gas Safe registration.",
        faqs=[("Do I need a separate page for each plumbing service?", "Yes. Separate pages for leaks, drains, boilers, bathrooms and emergency callouts match specific searches and convert better than one general page."),
              ("How can plumbers rank in several towns?", "Create genuinely useful pages for each town with real local details, and support them with citations and reviews from those areas.")]),
    "Dental Clinics": dict(
        title="Dental SEO: Attract Patients Searching for Treatments Near Them",
        text="Patients search by treatment and location, such as “dental implants in Leeds”, “emergency dentist near me” and “teeth whitening Chicago”. Give each treatment its own page with clear pricing guidance, FAQs and before-and-after information, and have content reviewed by your dentists. Show GDC registration in the UK or state licence details in the USA.",
        faqs=[("Which dental treatments should have their own page?", "Create pages for your highest-value treatments, such as implants, orthodontics, cosmetic dentistry and emergency care, plus general check-ups."),
              ("How do dental clinics get more Google reviews?", "Ask every happy patient after their appointment with a direct review link by SMS or email, and reply to every review professionally.")]),
    "Law Firms": dict(
        title="Law Firm SEO: Get Found by Clients Who Need a Lawyer Now",
        text="Clients search by practice area and place, for example “employment solicitor Manchester” or “car accident lawyer Houston”. Build detailed practice area pages, attorney profiles with credentials, case-type FAQs and a local page for each office, all written in line with your regulator’s advertising rules.",
        faqs=[("What content works best for law firm websites?", "Practice area pages, attorney profiles, plain-language guides to legal processes and case-type FAQs usually perform best."),
              ("Can law firms advertise freely online?", "No. Advertising is regulated, so we keep content factual and compliant with your regulator’s rules, and your team should approve it before publishing.")]),
    "Real Estate Agencies": dict(
        title="Real Estate SEO: Beat the Portals with Local Search",
        text="Agencies beat the portals by owning neighbourhood searches such as “homes for sale in [area]” and “estate agents in [town]”. Publish area guides, local market updates and free valuation landing pages, and keep listing pages clean so they do not create duplicate content.",
        faqs=[("How can an agency compete with Zillow or Rightmove?", "Focus on hyper-local content, valuation pages, agent expertise and reviews, which portals cannot match for individual neighbourhoods."),
              ("What pages should a real estate website have?", "Area guides, valuation pages, buyer and seller guides, agent profiles and clean listing pages with unique descriptions.")]),
    "Construction Companies": dict(
        title="Construction SEO: Win Commercial and Residential Projects",
        text="Buyers search by project type and region. Build pages for each type, such as extensions, new builds and commercial fit-outs, with case studies that show scope, timeline and location. Display accreditations, safety credentials and insurance so decision-makers can shortlist you quickly.",
        faqs=[("Does SEO work for large construction projects?", "Yes. Decision-makers research contractors online, so strong case studies and service pages help you reach the shortlist before a tender begins."),
              ("What should construction case studies include?", "Scope, location, timeline, challenges, results and photos, written so that a prospect can picture a similar project with you.")]),
    "SaaS Companies": dict(
        title="SaaS SEO: Turn Problem-Aware Searches into Trials and Demos",
        text="SaaS SEO captures people who are searching for a problem or a solution. Build use-case pages, integration pages, comparison and “alternative to” pages, and helpful documentation-style content. Technical SEO matters too, because JavaScript-heavy sites need correct rendering and clean internal linking.",
        faqs=[("Which SaaS pages usually convert best?", "Use-case pages, comparison and alternatives pages, pricing pages and integration pages typically capture the most ready-to-buy searches."),
              ("Is SaaS SEO different from other SEO?", "Yes. It has longer sales cycles, more technical considerations and a stronger need for content that matches each stage of the buying journey.")]),
    "D2C Brands": dict(
        title="D2C SEO: Grow Direct Sales Without Relying on Ads",
        text="Direct-to-consumer brands lower their ad spend by ranking for category, product and problem-led searches. Optimise collection and product pages, publish buying guides that answer pre-purchase questions, and build brand searches through reviews and PR.",
        faqs=[("How does SEO help a D2C brand?", "SEO brings in shoppers at a lower acquisition cost than paid ads and builds lasting visibility for category, product and brand searches."),
              ("Which pages should a D2C brand optimise first?", "Start with your best-selling collection pages and products, then add guides and comparison content that supports them.")]),
    "Solar Installation Companies": dict(
        title="Solar Installer SEO: Capture Homeowners Researching Solar",
        text="Solar buyers research costs, savings and incentives before requesting quotes. Create pages for residential, commercial and battery storage services, local installer pages and cost guides. Incentives and grants differ by country and change often, so keep those pages up to date and refer to official sources.",
        faqs=[("What content do solar customers want to read?", "Cost guides, savings explanations, installation process pages, system size guides and local case studies all help buyers decide."),
              ("How can installers stand out from comparison sites?", "Publish original local case studies, transparent pricing guidance and verified reviews that comparison sites cannot replicate.")]),
    "Solar Energy Companies": dict(
        title="Solar Energy Company SEO: Rank for Installation and Cost Searches",
        text="Solar energy buyers search for costs, savings and installers in their area. Build clear pages for each service, publish local case studies, and keep pages about incentives accurate, since rules differ between the UK and USA and change over time.",
        faqs=[("Which solar keywords should I target?", "Target installation, cost, battery storage and commercial solar terms combined with the cities and regions you serve."),
              ("Does content about incentives help rankings?", "Accurate, regularly updated incentive content can attract high-intent visitors, provided it cites official sources and is reviewed often.")]),
    "Recruitment Agencies": dict(
        title="Recruitment Agency SEO: Attract Both Employers and Candidates",
        text="Recruitment agencies serve two audiences. Build sector and location pages for employers, such as “IT recruitment agency London”, and job-category pages and career guides for candidates. Salary guides and hiring advice earn links and build authority. Keep job content fresh and structured so search engines can show it.",
        faqs=[("Should a recruitment website target employers or candidates?", "Both. Employer pages generate client leads, while candidate content builds your talent pool, so the strategy should serve each separately."),
              ("What content earns links for recruiters?", "Salary guides, hiring trend reports and market insight articles tend to earn links and mentions from industry publications.")]),
    "Accounting Firms": dict(
        title="Accountant SEO: Win Clients Searching for Tax and Business Help",
        text="Clients search by service and place, for example “small business accountant Bristol” or “CPA near me”. Create pages for tax, bookkeeping, payroll and advisory, and publish up-to-date guides around key deadlines. Show professional memberships and client reviews to build trust.",
        faqs=[("Which accounting services should have their own page?", "Create pages for tax returns, bookkeeping, payroll, company accounts and advisory, then add pages for each industry or client type you serve."),
              ("Is deadline content worth publishing?", "Yes. Guides around tax deadlines attract timely, high-intent searches and bring in clients who need help right away, as long as they are kept up to date.")]),
}

PROPER = {"Italian", "Indian", "Chinese", "Mexican", "Umrah", "Hajj"}

SERVICE_LINKS = [("Local SEO", "local-seo-services.html"),
                 ("Technical SEO", "technical-seo-services.html"),
                 ("Ecommerce SEO", "ecommerce-seo-services.html"),
                 ("Link Building", "link-building-services.html"),
                 ("SEO Content Marketing", "content-marketing-services.html")]
COUNTRY_LINKS = [("SEO Company UK", "seo-company-uk.html"),
                 ("SEO Company USA", "seo-company-usa.html"),
                 ("SEO Company India", "seo-company-india.html")]


def esc(s):
    return html.escape(s, quote=True)


def clean(name):
    return re.sub(r"\s*\(.*?\)", "", name).strip()


def lc(name):
    out = []
    for w in name.split():
        caps = sum(1 for c in w if c.isupper())
        if w in PROPER or caps >= 2 or any(c.isdigit() for c in w):
            out.append(w)
        else:
            out.append(w.lower())
    return " ".join(out)


def slugify(name):
    s = name.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def pick(slug, n):
    return int(hashlib.md5(slug.encode()).hexdigest(), 16) % n


def trunc(s, n):
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0].rstrip(",;:") + "…"


HEAD = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="stylesheet" href="assets/css/style.css">
{ld}</head>
<body data-no-brand>
<main id="main">
"""
TAIL = """</main>
<script src="assets/js/config.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>
"""


def faq_ld(faqs):
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    return '  <script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>\n"


def faq_html(faqs):
    out = []
    for i, (q, a) in enumerate(faqs):
        out.append("      <details%s><summary>%s</summary><p>%s</p></details>" % (" open" if i == 0 else "", esc(q), a if "<a " in a else esc(a)))
    return "\n".join(out)


def pills(items, cls="pills"):
    return '<ul class="%s">' % cls + "".join('<li><a href="%s">%s</a></li>' % (h, esc(t)) for t, h in items) + "</ul>"


def related_links(local_type):
    blog = [("Local SEO checklist", "blog-local-seo-checklist.html")] if local_type in ("local", "hybrid") else [("Technical SEO audit guide", "blog-technical-seo-audit-guide.html")]
    blog += [("What is SEO?", "blog-what-is-seo-and-how-it-works.html"), ("How to choose an SEO company", "blog-how-to-choose-seo-company.html")]
    return blog


def related_block(cattype, extra_first=None):
    items = list(SERVICE_LINKS) + COUNTRY_LINKS + related_links(cattype) + [("All industries", "industries.html")]
    return pills(items)


def services_html(stype, n, nl, kw):
    rows = []
    for t, href, txt in SERVICES[stype]:
        rows.append('        <li><strong><a href="%s">%s</a>:</strong> %s</li>' % (href, esc(t), esc(txt.format(n=n, nl=nl, kw=kw))))
    return '      <ul class="checklist">\n' + "\n".join(rows) + "\n      </ul>"


def steps_html(nl):
    return """      <ol class="steps">
        <li><h3>Audit</h3><p>We review your website, rankings and competitors in the %s sector to find the fastest wins.</p></li>
        <li><h3>Strategy</h3><p>We choose the keywords, pages and locations that bring the most valuable enquiries.</p></li>
        <li><h3>Execute</h3><p>We optimise pages, publish content, fix technical issues and earn links every month.</p></li>
        <li><h3>Report</h3><p>You see rankings, traffic, calls and leads in plain language, with clear next steps.</p></li>
      </ol>""" % esc(nl)


def cta_band(title, text):
    return """  <section class="section">
    <div class="container"><div class="cta-band">
      <h2>%s</h2>
      <p>%s</p>
      <p><a class="btn btn-light" data-cfg-href="tel" href="#"><span data-cfg="phoneDisplay"></span></a> <a class="btn btn-wa" data-cfg-href="wa" href="#">WhatsApp</a> <a class="btn btn-primary" href="contact.html#quote">Free SEO Audit</a></p>
    </div></div>
  </section>
""" % (esc(title), esc(text))


def build_niche(cat, sub, subs_of_cat, hub_file):
    n = clean(sub)
    nl = lc(n)
    uk_only = "(UK)" in sub
    c = CAT[cat["num"]]
    stype = c["type"]
    slug = slugify(n)
    fname = "seo-for-%s.html" % slug
    mk = "the UK" if uk_only else "the UK and USA"
    mk_short = "the UK" if uk_only else "the UK & USA"

    kws = [(k.format(n=nl), i) for k, i in KEYWORDS[stype]]
    if uk_only:
        kws = [(k, i) for k, i in kws if "USA" not in k and "New York" not in k and "usa" not in k.lower()]
        kws.append(("%s in Manchester" % nl, "Local intent (UK)"))
    kw1 = kws[0][0]
    kw2 = kws[1][0]

    title = "%s SEO Services in %s" % (n, mk_short)
    title = title if len(title) <= 62 else "%s SEO Services UK & USA" % n
    desc = "SEO services for %s in %s. Local SEO, technical fixes, content and link building that bring in more enquiries. Get a free SEO audit." % (nl, mk_short)
    desc = trunc(desc, 158)

    intros = [
        "Whether you run a single location or a growing national brand, competing in the %s sector means being found on Google at the exact moment customers search. We build SEO strategies that turn those searches into calls, WhatsApp chats and form enquiries." % nl,
        "Most %s start their search for %s on Google, and the businesses on page one capture the majority of the clicks. Our SEO services help businesses in the %s sector across %s rank for the terms that bring ready-to-buy customers." % (c["buyers"], nl, nl, mk),
        "Search is where customers compare %s providers before they get in touch. If your website does not appear for the right searches, those enquiries go to your competitors. We fix that with focused, measurable SEO built for %s." % (nl, mk),
    ]
    intro = intros[pick(slug, 3)]

    pr = PRIORITY.get(n)
    faqs = []
    if pr:
        faqs += pr["faqs"]
    faqs += [
        ("How long does SEO take to work for %s?" % nl, "Most businesses see early movement in rankings and traffic within 3 to 4 months, and stronger lead growth between months 4 and 8. Highly competitive terms and new websites can take longer. We set realistic milestones after your free audit."),
        ("What is included in SEO services for %s?" % nl, "Keyword research, on-page optimisation, technical fixes, content creation, link building and monthly reporting, all adapted to %s customers.%s" % (nl, " For local businesses we also manage your Google Business Profile, citations and reviews." if stype in ("local", "hybrid") else "")),
        (("Can you help with SEO for %s in the UK?" % nl) if uk_only else ("Can you help %s in both the UK and USA?" % nl),
         "Yes. We research each market separately, using local spelling, cities, directories and search habits, so your pages match what customers in each country actually type." if not uk_only else "Yes. We research the UK market in detail, using British spelling, local cities, directories and search habits."),
        ("How much does SEO for %s cost?" % nl, "Cost depends on competition, the number of locations, your website’s condition and your goals. After a free audit we send a clear proposal with no hidden fees. Use the form on this page to request yours."),
    ]

    rows = "\n".join("          <tr><td>%s</td><td>%s</td></tr>" % (esc(k), esc(i)) for k, i in kws)

    sibs = [(clean(s), "seo-for-%s.html" % slugify(clean(s))) for s in subs_of_cat if clean(s) != n]
    cat_name = c["short"]
    hub_title = cat_name

    p = []
    p.append(HEAD.format(title=esc(title), desc=esc(desc), ld=faq_ld(faqs)))
    p.append("""  <section class="page-hero"><div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><a href="industries.html">Industries</a><span>/</span><a href="%s">%s</a><span>/</span>%s</nav>
    <h1>SEO Services for %s in %s</h1>
    <p class="lead">Rank higher for searches such as “%s” and “%s”, and turn organic traffic into calls, WhatsApp chats and enquiries across %s.</p>
  </div></section>
""" % (hub_file, esc(hub_title), esc(n), esc(n), mk, esc(kw1), esc(kw2), mk))

    p.append("""  <section class="section"><div class="container split">
    <div class="prose" style="margin:0">
      <p>%s</p>
      <h2>Why SEO Matters for %s</h2>
      <p>%s</p>
      <h2>SEO Challenges for %s</h2>
      <ul>
%s
      </ul>
%s
%s
      <h2>Our SEO Services for %s</h2>
%s
    </div>
    <div class="sticky-side" data-lead-form data-source="%s" data-title="Get a Free SEO Audit for %s" data-subtitle="Tell us about your business and we will send an action plan within one business day."></div>
  </div></section>
""" % (
        esc(intro), esc(n), esc(c["why"]), esc(n),
        "\n".join("        <li>%s</li>" % esc(x) for x in c["challenges"]),
        ('      <p class="notice"><strong>Compliance note:</strong> %s</p>' % esc(c["note"])) if c["note"] else "",
        ("      <h2>%s</h2>\n      <p>%s</p>" % (esc(pr["title"]), esc(pr["text"]))) if pr else "",
        esc(n), services_html(stype, n, nl, kw1), esc("Niche: " + n), esc(n)))

    p.append("""  <section class="section section-alt"><div class="container">
    <div class="section-head">
      <h2>What Customers Search For in the %s Sector</h2>
      <p>These are typical search patterns we target. We confirm real demand and difficulty with keyword research tools before building your plan.</p>
    </div>
    <div class="table-wrap" style="max-width:760px;margin:0 auto">
      <table>
        <thead><tr><th>Example search</th><th>What it tells us</th></tr></thead>
        <tbody>
%s
        </tbody>
      </table>
    </div>
  </div></section>
""" % (esc(nl), rows))

    uk_card = """<div class="card"><h3>SEO for %s in the UK</h3><p>British spelling, UK cities and directories, and search habits specific to UK customers. See our <a href="seo-company-uk.html">SEO company in the UK</a>.</p></div>""" % esc(n)
    us_card = """<div class="card"><h3>SEO for %s in the USA</h3><p>American English, state and city targeting, and US directories and review platforms. See our <a href="seo-company-usa.html">SEO company in the USA</a>.</p></div>""" % esc(n)
    cards = uk_card if uk_only else uk_card + "\n      " + us_card
    p.append("""  <section class="section"><div class="container">
    <div class="section-head">
      <h2>SEO for %s in %s</h2>
      <p>Each market has its own keywords, competitors and customer expectations, so we plan them separately.</p>
    </div>
    <div class="grid grid-2">
      %s
    </div>
  </div></section>
""" % (esc(n), mk, cards))

    p.append("""  <section class="section section-alt"><div class="container">
    <div class="section-head"><h2>How We Get %s More Leads</h2></div>
%s
  </div></section>
""" % (esc(n), steps_html(nl)))

    p.append("""  <section class="section"><div class="container faq" style="max-width:820px">
    <div class="section-head"><h2>FAQs: SEO for %s</h2></div>
%s
  </div></section>
""" % (esc(n), faq_html(faqs)))

    p.append("""  <section class="section section-alt"><div class="container">
    <div class="section-head"><h2>More %s SEO Services</h2><p>Explore related niches in this category, or return to the <a href="%s">%s overview</a>.</p></div>
    %s
  </div></section>
""" % (esc(cat_name), hub_file, esc(cat_name), pills(sibs)))

    p.append("""  <section class="section"><div class="container">
    <div class="section-head"><h2>Related Services and Resources</h2></div>
    %s
  </div></section>
""" % related_block(stype))

    p.append(cta_band("Ready to Get More %s Customers from Google?" % n, "Call us, message us on WhatsApp or request a free SEO audit. We will review your website and share clear next steps."))
    p.append(TAIL)
    return fname, "".join(p)


def build_hub(cat, all_cats):
    c = CAT[cat["num"]]
    stype = c["type"]
    name = c["short"]
    nl = lc(name)
    fname = "seo-for-%s.html" % c["slug"]
    subs = [(clean(s), "seo-for-%s.html" % slugify(clean(s))) for s in cat["subs"]]
    first = [s[0] for s in subs[:3]]
    kw1 = KEYWORDS[stype][0][0].format(n=lc(subs[0][0]))
    kw2 = KEYWORDS[stype][1][0].format(n=lc(subs[1][0]))

    title = "%s SEO Services in the UK & USA" % name
    desc = trunc("SEO services for %s businesses in the UK and USA, from %s to %s. Local SEO, technical SEO, content and link building. Free audit." % (nl, lc(first[0]), lc(first[1])), 158)

    faqs = [
        ("What SEO services do you offer for %s businesses?" % nl, "We offer local SEO, technical SEO, content marketing, link building and conversion tracking, adapted to the way customers search in the %s sector." % nl),
        ("Which %s niches do you cover?" % nl, "We cover %d niches in this category, including %s, %s and %s. Each has its own page with niche-specific search terms and strategy." % (len(subs), lc(first[0]), lc(first[1]), lc(first[2]))),
        ("Do you work in both the UK and the USA?", "Yes. We plan UK and US campaigns separately, with local spelling, cities, directories and competitors for each market."),
        ("How do I get started?", "Request a free SEO audit using the form on this page, or call or message us on WhatsApp. We review your website and send a clear plan."),
    ]

    cards = "\n".join('      <a class="niche-card" href="%s"><strong>%s</strong><span>SEO services &rarr;</span></a>' % (h, esc(t)) for t, h in subs)
    others = [(CAT[o["num"]]["short"], "seo-for-%s.html" % CAT[o["num"]]["slug"]) for o in all_cats if o["num"] != cat["num"]]

    p = []
    p.append(HEAD.format(title=esc(title), desc=esc(desc), ld=faq_ld(faqs)))
    p.append("""  <section class="page-hero"><div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><a href="industries.html">Industries</a><span>/</span>%s</nav>
    <h1>%s SEO Services in the UK and USA</h1>
    <p class="lead">Get found for searches such as “%s” and “%s”. We help %s businesses across %d niches turn Google rankings into enquiries.</p>
  </div></section>
""" % (esc(name), esc(name), esc(kw1), esc(kw2), esc(nl), len(subs)))

    p.append("""  <section class="section"><div class="container split">
    <div class="prose" style="margin:0">
      <h2>Why SEO Matters in the %s Sector</h2>
      <p>%s</p>
      <h2>SEO Challenges for %s Businesses</h2>
      <ul>
%s
      </ul>
%s
      <h2>Our SEO Services for %s Businesses</h2>
%s
    </div>
    <div class="sticky-side" data-lead-form data-source="%s" data-title="Get a Free %s SEO Audit" data-subtitle="Tell us about your business and we will send an action plan within one business day."></div>
  </div></section>
""" % (esc(nl), esc(c["why"]), esc(nl),
       "\n".join("        <li>%s</li>" % esc(x) for x in c["challenges"]),
       ('      <p class="notice"><strong>Compliance note:</strong> %s</p>' % esc(c["note"])) if c["note"] else "",
       esc(nl), services_html(stype, name, nl, kw1), esc("Category: " + name), esc(name)))

    p.append("""  <section class="section section-alt"><div class="container">
    <div class="section-head">
      <h2>%s SEO Services by Niche</h2>
      <p>Choose your niche to see search terms, challenges and a tailored SEO approach.</p>
    </div>
    <div class="niche-grid">
%s
    </div>
  </div></section>
""" % (esc(name), cards))

    p.append("""  <section class="section"><div class="container">
    <div class="section-head"><h2>How We Get %s Businesses More Leads</h2></div>
%s
  </div></section>
""" % (esc(nl), steps_html(nl)))

    p.append("""  <section class="section section-alt"><div class="container faq" style="max-width:820px">
    <div class="section-head"><h2>FAQs: %s SEO</h2></div>
%s
  </div></section>
""" % (esc(name), faq_html(faqs)))

    p.append("""  <section class="section"><div class="container">
    <div class="section-head"><h2>Explore Other Industries</h2></div>
    %s
    <p style="text-align:center;margin-top:22px"><a class="btn btn-outline" href="industries.html">View All Industries</a></p>
  </div></section>

  <section class="section section-alt"><div class="container">
    <div class="section-head"><h2>Related Services and Resources</h2></div>
    %s
  </div></section>
""" % (pills(others), related_block(stype)))

    p.append(cta_band("Ready to Grow Your %s Business with SEO?" % name, "Call us, message us on WhatsApp or request a free SEO audit. We will review your website and share clear next steps."))
    p.append(TAIL)
    return fname, "".join(p)


def build_index(cats):
    total = sum(len(c["subs"]) for c in cats)
    title = "SEO Services by Industry: %d+ Niches in the UK & USA" % (total // 10 * 10)
    desc = trunc("Find SEO services for your industry. %d niches in the UK and USA, from travel and healthcare to law, construction, ecommerce and SaaS." % total, 158)
    faqs = [
        ("Which industries do you provide SEO for?", "We provide SEO for %d niches across %d categories, including travel, healthcare, legal, finance, real estate, construction, automotive, education, ecommerce, hospitality, beauty, technology and more." % (total, len(cats))),
        ("Do you work with businesses in both the UK and USA?", "Yes. We plan each market separately, using local spelling, cities, directories and competitors."),
        ("What if my niche is not listed?", "Contact us. We can research your niche and build a custom SEO plan for it."),
    ]
    p = [HEAD.format(title=esc(title), desc=esc(desc), ld=faq_ld(faqs))]
    p.append("""  <section class="page-hero"><div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span>Industries</nav>
    <h1>SEO Services by Industry in the UK and USA</h1>
    <p class="lead">Choose your industry to see how we help %d types of business rank higher on Google and win more customers.</p>
  </div></section>
""" % total)
    p.append('  <section class="section"><div class="container">\n')
    for c in cats:
        d = CAT[c["num"]]
        subs = [(clean(s), "seo-for-%s.html" % slugify(clean(s))) for s in c["subs"]]
        p.append("""    <div class="card" style="margin-bottom:22px">
      <h2 style="font-size:1.4rem"><a href="seo-for-%s.html" style="text-decoration:none">%s SEO Services</a></h2>
      %s
      <p style="margin:14px 0 0"><a class="more" href="seo-for-%s.html"><strong>View all %s niches &rarr;</strong></a></p>
    </div>
""" % (d["slug"], esc(d["short"]), pills(subs), d["slug"], esc(d["short"])))
    p.append("  </div></section>\n\n")
    p.append("""  <section class="section section-alt"><div class="container faq" style="max-width:820px">
    <div class="section-head"><h2>Industry SEO FAQs</h2></div>
%s
  </div></section>
""" % faq_html(faqs))
    p.append("""  <section class="section"><div class="container">
    <div class="section-head"><h2>Related Services</h2></div>
    %s
  </div></section>
""" % pills(list(SERVICE_LINKS) + COUNTRY_LINKS + [("SEO Blog", "blog.html")]))
    p.append(cta_band("Do Not See Your Industry?", "Tell us about your business. We will research your niche and build a custom SEO plan."))
    p.append(TAIL)
    return "industries.html", "".join(p)


def update_main_js(cats):
    path = os.path.join(ROOT, "assets", "js", "main.js")
    src = open(path, encoding="utf-8").read()
    arr = ",\n    ".join('["%s", "%s"]' % (CAT[c["num"]]["slug"], CAT[c["num"]]["short"]) for c in cats)
    block = "/* INDUSTRIES:START */\n  var industries = [\n    %s\n  ];\n  /* INDUSTRIES:END */" % arr
    new, k = re.subn(r"/\* INDUSTRIES:START \*/.*?/\* INDUSTRIES:END \*/", lambda m: block, src, flags=re.S)
    assert k == 1, "INDUSTRIES markers missing in main.js"
    open(path, "w", encoding="utf-8").write(new)


def write_picker_data(cats):
    data = []
    for c in cats:
        d = CAT[c["num"]]
        data.append({"name": d["short"], "file": "seo-for-%s.html" % d["slug"],
                     "niches": [[clean(x), "seo-for-%s.html" % slugify(clean(x))] for x in c["subs"]]})
    path = os.path.join(ROOT, "assets", "js", "industry-data.js")
    open(path, "w", encoding="utf-8").write(
        "/* Generated by tools/generate_niche_pages.py. Do not edit by hand. */\nwindow.SITE_NICHES = %s;\n" % json.dumps(data, ensure_ascii=False))


def main():
    cats = json.load(open(os.path.join(TOOLS, "categories.json"), encoding="utf-8"))
    seen = {}
    pages = {}
    for cat in cats:
        hub_file, hub_html = build_hub(cat, cats)
        assert hub_file not in pages, hub_file
        pages[hub_file] = hub_html
        for sub in cat["subs"]:
            f, h = build_niche(cat, sub, cat["subs"], hub_file)
            assert f not in pages, "duplicate page name: " + f
            pages[f] = h
    f, h = build_index(cats)
    pages[f] = h
    for f, h in pages.items():
        open(os.path.join(ROOT, f), "w", encoding="utf-8").write(h)
    update_main_js(cats)
    write_picker_data(cats)
    print("Generated %d pages (%d hubs, %d niches, 1 index)" % (len(pages), len(cats), sum(len(c["subs"]) for c in cats)))


if __name__ == "__main__":
    main()
