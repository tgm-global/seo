/*
 * Shared site script.
 * Reads window.SITE_CONFIG (assets/js/config.js) and:
 *  - injects the fixed header, fixed footer bar and full footer
 *  - fills every [data-cfg] element with config values
 *  - renders lead forms (Web3Forms) and testimonials
 *  - adds canonical, Open Graph and JSON-LD structured data
 */
(function () {
  "use strict";

  var C = window.SITE_CONFIG || {};
  var D = document;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  var telHref = "tel:" + (C.phoneRaw || "");
  var waHref = "https://wa.me/" + (C.whatsappNumber || "") + "?text=" + encodeURIComponent(C.whatsappMessage || "");
  var mailHref = "mailto:" + (C.email || "");
  var baseUrl = String(C.siteUrl || "").replace(/\/+$/, "");
  var current = location.pathname.split("/").pop() || "index.html";

  var ICON = {
    phone: '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
    wa: '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>',
    mail: '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="22,6 12,13 2,6"/></svg>'
  };

  var services = [
    ["local-seo-services.html", "Local SEO"],
    ["technical-seo-services.html", "Technical SEO"],
    ["ecommerce-seo-services.html", "Ecommerce SEO"],
    ["link-building-services.html", "Link Building"],
    ["content-marketing-services.html", "SEO Content Marketing"]
  ];
  var locations = [
    ["seo-company-uk.html", "SEO Company UK"],
    ["seo-company-usa.html", "SEO Company USA"],
    ["seo-company-india.html", "SEO Company India"]
  ];

  function navLink(href, label) {
    var cur = href === current || (current === "" && href === "index.html");
    return '<a href="' + href + '"' + (cur ? ' aria-current="page"' : "") + ">" + esc(label) + "</a>";
  }

  function buildHeader() {
    var subServices = services.map(function (s) { return "<li>" + navLink(s[0], s[1]) + "</li>"; }).join("");
    var subLoc = locations.map(function (s) { return "<li>" + navLink(s[0], s[1]) + "</li>"; }).join("");
    return (
      '<a class="skip-link" href="#main">Skip to content</a>' +
      '<header class="site-header"><div class="container header-inner">' +
      '<a class="brand" href="index.html" aria-label="' + esc(C.companyName) + ' home"><span class="brand-mark" aria-hidden="true">&#9650;</span><span>' + esc(C.companyName) + "</span></a>" +
      '<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="Toggle navigation"><span></span></button>' +
      '<nav id="primary-nav" class="primary-nav" aria-label="Primary"><ul>' +
      "<li>" + navLink("index.html", "Home") + "</li>" +
      '<li class="has-sub">' + navLink("services.html", "Services") + '<ul class="sub">' + subServices + "</ul></li>" +
      '<li class="has-sub"><a href="seo-company-usa.html">Locations</a><ul class="sub">' + subLoc + "</ul></li>" +
      "<li>" + navLink("about.html", "About") + "</li>" +
      "<li>" + navLink("blog.html", "Blog") + "</li>" +
      "<li>" + navLink("contact.html", "Contact") + "</li>" +
      "</ul>" +
      '<div class="header-cta">' +
      '<a class="btn btn-call btn-sm" href="' + telHref + '">' + ICON.phone + '<span class="txt">' + esc(C.phoneDisplay) + "</span></a>" +
      '<a class="btn btn-wa btn-sm" href="' + waHref + '" target="_blank" rel="noopener">' + ICON.wa + "<span>WhatsApp</span></a>" +
      "</div></nav></div></header>"
    );
  }

  function buildStickyFooter() {
    return (
      '<div class="sticky-footer" role="complementary" aria-label="Quick contact"><div class="container">' +
      '<span class="sf-note">Talk to an SEO expert today</span>' +
      '<a class="btn btn-call" href="' + telHref + '">' + ICON.phone + "<span>Call</span></a>" +
      '<a class="btn btn-wa" href="' + waHref + '" target="_blank" rel="noopener">' + ICON.wa + "<span>WhatsApp</span></a>" +
      '<a class="btn btn-primary" href="contact.html#quote"><span>Free SEO Audit</span></a>' +
      "</div></div>"
    );
  }

  function buildFooter() {
    var s = C.social || {};
    var social = [["linkedin", "LinkedIn"], ["facebook", "Facebook"], ["instagram", "Instagram"], ["x", "X"]]
      .filter(function (p) { return s[p[0]]; })
      .map(function (p) { return '<a href="' + esc(s[p[0]]) + '" target="_blank" rel="noopener me">' + p[1] + "</a>"; })
      .join("");
    var a = C.address || {};
    var addr = [a.street, a.city, a.region, a.postalCode, a.country].filter(Boolean).join(", ");
    return (
      '<footer class="site-footer"><div class="container">' +
      '<div class="footer-grid">' +
      '<div><span class="footer-brand">' + esc(C.companyName) + "</span><p>" + esc(C.tagline) + ".</p>" +
      (social ? '<div class="social">' + social + "</div>" : "") + "</div>" +
      "<div><h4>Services</h4><ul>" + services.map(function (x) { return '<li><a href="' + x[0] + '">' + x[1] + "</a></li>"; }).join("") + "</ul></div>" +
      "<div><h4>Company</h4><ul>" +
      '<li><a href="about.html">About Us</a></li><li><a href="blog.html">SEO Blog</a></li><li><a href="contact.html">Contact</a></li>' +
      locations.map(function (x) { return '<li><a href="' + x[0] + '">' + x[1] + "</a></li>"; }).join("") +
      "</ul></div>" +
      "<div><h4>Contact</h4><ul>" +
      '<li><a href="' + telHref + '">' + esc(C.phoneDisplay) + "</a></li>" +
      '<li><a href="' + waHref + '" target="_blank" rel="noopener">WhatsApp us</a></li>' +
      '<li><a href="' + mailHref + '">' + esc(C.email) + "</a></li>" +
      (addr ? "<li>" + esc(addr) + "</li>" : "") +
      "</ul></div></div>" +
      '<div class="footer-bottom"><span>&copy; ' + new Date().getFullYear() + " " + esc(C.companyName) + ". All rights reserved.</span>" +
      '<span><a href="privacy-policy.html">Privacy Policy</a> &middot; <a href="terms.html">Terms</a></span></div>' +
      "</div></footer>"
    );
  }

  /* ---------- Lead form (Web3Forms) ---------- */
  function buildForm(source, title, subtitle) {
    return (
      '<form class="lead-form" novalidate data-source="' + esc(source) + '">' +
      "<h3>" + esc(title) + "</h3>" +
      '<p class="sub-text">' + esc(subtitle) + "</p>" +
      '<input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">' +
      '<div class="field"><label>Full name *</label><input name="name" type="text" autocomplete="name" required></div>' +
      '<div class="form-row">' +
      '<div class="field"><label>Email *</label><input name="email" type="email" autocomplete="email" required></div>' +
      '<div class="field"><label>Phone / WhatsApp *</label><input name="phone" type="tel" autocomplete="tel" required></div>' +
      "</div>" +
      '<div class="form-row">' +
      '<div class="field"><label>Country *</label><select name="country" required><option value="">Select country</option><option>United Kingdom</option><option>United States</option><option>India</option><option>Other</option></select></div>' +
      '<div class="field"><label>Website URL</label><input name="website" type="url" placeholder="https://"></div>' +
      "</div>" +
      '<div class="field"><label>Service needed</label><select name="service"><option>SEO audit</option><option>Local SEO</option><option>Technical SEO</option><option>Ecommerce SEO</option><option>Link building</option><option>Content marketing</option><option>Not sure yet</option></select></div>' +
      '<div class="field"><label>How can we help?</label><textarea name="message" placeholder="Tell us about your business and goals"></textarea></div>' +
      '<button class="btn btn-primary btn-block" type="submit">Get My Free SEO Audit</button>' +
      '<p class="form-status" role="status" aria-live="polite"></p>' +
      '<p class="form-note">We reply within one business day. Your details are never shared or sold.</p>' +
      "</form>"
    );
  }

  function initForms() {
    var holders = D.querySelectorAll("[data-lead-form]");
    Array.prototype.forEach.call(holders, function (h) {
      var title = h.getAttribute("data-title") || "Get a Free SEO Audit";
      var sub = h.getAttribute("data-subtitle") || "Share your details and we will send a clear action plan.";
      h.innerHTML = buildForm(h.getAttribute("data-source") || current, title, sub);
      var form = h.querySelector("form");
      var status = form.querySelector(".form-status");
      var btn = form.querySelector("button[type=submit]");

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        status.className = "form-status";
        status.textContent = "";

        if (!form.checkValidity()) {
          status.className = "form-status err";
          status.textContent = "Please fill in all required fields with valid details.";
          form.reportValidity && form.reportValidity();
          return;
        }
        var key = C.web3formsKey || "";
        if (!key || key.indexOf("YOUR_") === 0) {
          status.className = "form-status err";
          status.textContent = "The form is not connected yet. Please call or WhatsApp us instead.";
          return;
        }

        var data = new FormData(form);
        var payload = {
          access_key: key,
          subject: "New SEO enquiry from " + (C.companyName || "website"),
          from_name: (C.companyName || "Website") + " Lead Form",
          botcheck: data.get("botcheck") ? true : "",
          name: data.get("name"),
          email: data.get("email"),
          phone: data.get("phone"),
          country: data.get("country"),
          website: data.get("website"),
          service: data.get("service"),
          message: data.get("message"),
          page_url: location.href,
          form_source: form.getAttribute("data-source")
        };

        btn.disabled = true;
        var oldText = btn.textContent;
        btn.textContent = "Sending...";

        fetch("https://api.web3forms.com/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(payload)
        })
          .then(function (r) { return r.json(); })
          .then(function (res) {
            if (res && res.success) {
              status.className = "form-status ok";
              status.textContent = "Thank you! We have received your request.";
              form.reset();
              setTimeout(function () { location.href = "thank-you.html"; }, 600);
            } else {
              throw new Error((res && res.message) || "Submission failed");
            }
          })
          .catch(function () {
            status.className = "form-status err";
            status.textContent = "Something went wrong. Please call or WhatsApp us and we will help right away.";
          })
          .then(function () {
            btn.disabled = false;
            btn.textContent = oldText;
          });
      });
    });
  }

  /* ---------- Testimonials ---------- */
  function initTestimonials() {
    var holders = D.querySelectorAll("[data-testimonials]");
    var loadedScript = false;
    Array.prototype.forEach.call(holders, function (h) {
      var section = h.closest("section");
      var key = (C.testimonialsWebKey || "").trim();
      var list = C.testimonials || [];
      if (key) {
        h.innerHTML = '<div class="elfsight-app-' + esc(key) + '" data-elfsight-app-lazy></div>';
        if (!loadedScript) {
          var s = D.createElement("script");
          s.src = "https://elfsightcdn.com/platform.js";
          s.async = true;
          D.body.appendChild(s);
          loadedScript = true;
        }
      } else if (list.length) {
        h.className = (h.className + " grid grid-3").trim();
        h.innerHTML = list.map(function (t) {
          return '<figure class="card" style="margin:0"><blockquote style="margin:0 0 12px">&ldquo;' + esc(t.text) + '&rdquo;</blockquote><figcaption><strong>' +
            esc(t.name) + "</strong><br><span style=\"color:var(--muted);font-size:.9rem\">" + esc([t.role, t.country].filter(Boolean).join(" · ")) + "</span></figcaption></figure>";
        }).join("");
      } else if (section) {
        section.style.display = "none";
      }
    });
  }

  /* ---------- Config binders ---------- */
  function applyConfig() {
    Array.prototype.forEach.call(D.querySelectorAll("[data-cfg]"), function (el) {
      var k = el.getAttribute("data-cfg");
      if (C[k] != null) el.textContent = C[k];
    });
    Array.prototype.forEach.call(D.querySelectorAll("[data-cfg-href]"), function (el) {
      var t = el.getAttribute("data-cfg-href");
      if (t === "tel") el.href = telHref;
      if (t === "wa") { el.href = waHref; el.target = "_blank"; el.rel = "noopener"; }
      if (t === "mail") el.href = mailHref;
    });
  }

  /* ---------- SEO head tags ---------- */
  function setMeta(attr, name, content) {
    if (!content) return;
    var el = D.head.querySelector("meta[" + attr + '="' + name + '"]');
    if (!el) { el = D.createElement("meta"); el.setAttribute(attr, name); D.head.appendChild(el); }
    el.setAttribute("content", content);
  }
  function addLink(rel, href, extra) {
    var el = D.createElement("link");
    el.rel = rel; el.href = href;
    if (extra) Object.keys(extra).forEach(function (k) { el.setAttribute(k, extra[k]); });
    D.head.appendChild(el);
  }
  function addJsonLd(obj) {
    var s = D.createElement("script");
    s.type = "application/ld+json";
    s.text = JSON.stringify(obj);
    D.head.appendChild(s);
  }

  function seoHead() {
    var pageUrl = baseUrl + "/" + (current === "index.html" ? "" : current);
    if (!D.body.hasAttribute("data-no-brand") && C.companyName && D.title.indexOf(C.companyName) === -1) {
      D.title = D.title + " | " + C.companyName;
    }
    var desc = (D.head.querySelector('meta[name="description"]') || {}).content || "";
    addLink("canonical", pageUrl);
    setMeta("property", "og:title", D.title);
    setMeta("property", "og:description", desc);
    setMeta("property", "og:type", D.body.getAttribute("data-og-type") || "website");
    setMeta("property", "og:url", pageUrl);
    setMeta("property", "og:site_name", C.companyName);
    setMeta("name", "twitter:card", "summary");
    setMeta("name", "twitter:title", D.title);
    setMeta("name", "twitter:description", desc);

    var hl = {
      "seo-company-uk.html": "en-GB",
      "seo-company-usa.html": "en-US",
      "seo-company-india.html": "en-IN"
    };
    if (hl[current]) {
      Object.keys(hl).forEach(function (f) { addLink("alternate", baseUrl + "/" + f, { hreflang: hl[f] }); });
      addLink("alternate", baseUrl + "/", { hreflang: "x-default" });
    }

    var a = C.address || {};
    var s = C.social || {};
    var org = {
      "@context": "https://schema.org",
      "@type": "ProfessionalService",
      name: C.companyName,
      url: baseUrl + "/",
      telephone: C.phoneRaw,
      email: C.email,
      description: C.tagline,
      serviceType: "Search Engine Optimization",
      areaServed: [
        { "@type": "Country", name: "United Kingdom" },
        { "@type": "Country", name: "United States" },
        { "@type": "Country", name: "India" }
      ],
      sameAs: Object.keys(s).map(function (k) { return s[k]; }).filter(Boolean)
    };
    if (a.city || a.country) {
      org.address = { "@type": "PostalAddress", streetAddress: a.street || undefined, addressLocality: a.city || undefined, addressRegion: a.region || undefined, postalCode: a.postalCode || undefined, addressCountry: a.country || undefined };
    }
    addJsonLd(org);

    // Fill author/publisher for blog Article schema
    var art = D.getElementById("article-ld");
    if (art) {
      try {
        var d = JSON.parse(art.textContent);
        d.author = { "@type": "Organization", name: C.companyName };
        d.publisher = { "@type": "Organization", name: C.companyName };
        d.mainEntityOfPage = pageUrl;
        art.textContent = JSON.stringify(d);
      } catch (e) { /* ignore */ }
    }
  }

  /* ---------- Mobile nav ---------- */
  function initNav() {
    var toggle = D.querySelector(".nav-toggle");
    var nav = D.getElementById("primary-nav");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") { nav.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); }
    });
  }

  function init() {
    D.body.insertAdjacentHTML("afterbegin", buildHeader());
    D.body.insertAdjacentHTML("beforeend", buildFooter() + buildStickyFooter());
    applyConfig();
    initForms();
    initTestimonials();
    initNav();
    seoHead();
  }

  if (D.readyState === "loading") D.addEventListener("DOMContentLoaded", init);
  else init();
})();
