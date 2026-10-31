# SEO Company Lead Generation Website

A fast, static, SEO-friendly website for an SEO agency targeting the UK, USA and India.
No build step. Works directly on GitHub Pages.

## Change details from ONE place

Open `assets/js/config.js` and edit:

| Setting | What it updates |
|---|---|
| `companyName` | Header, footer, page titles, schema markup |
| `phoneDisplay` / `phoneRaw` | Header, fixed footer bar, footer, contact page |
| `whatsappNumber` / `whatsappMessage` | All WhatsApp buttons and links |
| `email` | Footer, contact page, privacy page |
| `web3formsKey` | Every enquiry form on every page |
| `testimonialsWebKey` | Testimonials widget on every page that has one |
| `testimonials` | Manual reviews (used when no widget key is set) |
| `siteUrl` | Canonical URLs, Open Graph, hreflang, schema |

## Fixed header and footer

- The header is fixed at the top and contains the phone number and WhatsApp button.
- A fixed bottom bar shows Call, WhatsApp and Free SEO Audit buttons on every page.
- A full link footer sits at the end of each page.

## Web3Forms setup

1. Get a free Access Key at https://web3forms.com
2. Paste it into `web3formsKey` in `assets/js/config.js`.

## Testimonials

Paste your widget key (for example an Elfsight app ID) into `testimonialsWebKey`.
If it is empty and `testimonials` is empty, the testimonials section is hidden automatically.
Only publish real client reviews.

## Publish on GitHub Pages

1. Create a GitHub repository and upload all files in this folder to the root.
2. Go to **Settings > Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/ (root)`, then Save.
4. Your site goes live at `https://your-username.github.io/your-repo/`.

## After going live

1. Set `siteUrl` in `assets/js/config.js` to your live URL.
2. Replace `https://your-username.github.io/your-repo` in `sitemap.xml` and `robots.txt` with the same URL (use find and replace).
3. Submit `sitemap.xml` in Google Search Console and Bing Webmaster Tools.
4. For a custom domain, add a `CNAME` file containing your domain.

## Adding a blog post

1. Copy any `blog-*.html` file and rename it.
2. Edit the title, meta description, `headline` and `datePublished` in the Article schema, and the content.
3. Add a card to `blog.html` and a line to `sitemap.xml`.

## Industry pages (350 niches)

Built from `tools/categories.json` (your categories PDF):

- `industries.html`: index of all industries
- `seo-for-<category>.html`: 20 category hub pages
- `seo-for-<niche>.html`: 350 niche pages (for example `seo-for-dental-clinics.html`)

Every niche page has its own title, description, H1/H2 headings based on search terms, search-term table, FAQs (with FAQ schema), breadcrumbs (with schema), a lead form, and links to its category hub, sibling niches, services, country pages and blog posts. The header, bottom bar and footer come from `assets/js/main.js`, so they stay fixed on every page.

### Add or rename a niche
1. Edit `tools/categories.json`.
2. Run `python3 tools/generate_niche_pages.py`
3. Run `python3 tools/make_sitemap.py`

### Sitemap
`python3 tools/make_sitemap.py` rebuilds `sitemap.xml` and `robots.txt` for every page. It reads `siteUrl` from `assets/js/config.js`, or pass your URL: `python3 tools/make_sitemap.py https://www.yourdomain.com`

## Pages

Home, Services hub, 5 service pages, 3 country pages (UK, USA, India with hreflang), About, Contact, Thank You, Blog index, 4 blog posts, Privacy Policy, Terms, 404, Industries index, 20 industry hubs and 350 niche pages (390 URLs in the sitemap).
