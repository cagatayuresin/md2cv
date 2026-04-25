(function () {
    'use strict';

    const DEFAULT_MARKDOWN = `---
name: "Jane Doe"
title: "Senior Software Engineer"
email: "jane.doe@example.com"
phone: "+1 555 010 0101"
location: "Berlin, Germany"
linkedin: "linkedin.com/in/janedoe"
github: "github.com/janedoe"
---

# Professional Summary

Backend engineer with a focus on distributed systems, observability, and developer experience.

# Work Experience

## Senior Software Engineer
**ExampleCo** | Remote | 2022 — Present

- Led the migration of the billing service to a Kafka-based event pipeline.
- Reduced p99 API latency by 38% through targeted caching and query optimization.
- Mentored four engineers and ran the team's hiring loop.

# Education

## B.Sc. Computer Science
**Example University** | 2015 — 2019

# Skills

| Area       | Tools                            |
|------------|----------------------------------|
| Languages  | Python, Go, TypeScript           |
| Platforms  | Docker, Kubernetes, AWS          |
| Datastores | PostgreSQL, Redis, ClickHouse    |
`;

    const editorEl = document.getElementById('md-editor');
    const previewFrame = document.getElementById('preview-frame');
    const templateSelect = document.getElementById('template-select');
    const convertBtn = document.getElementById('convert-btn');
    const alertContainer = document.getElementById('alert-container');
    const versionBadge = document.getElementById('version-badge');

    const editor = new EasyMDE({
        element: editorEl,
        autofocus: true,
        spellChecker: false,
        status: false,
        initialValue: DEFAULT_MARKDOWN,
        toolbar: [
            'bold', 'italic', 'heading', '|',
            'quote', 'unordered-list', 'ordered-list', 'table', '|',
            'link', 'horizontal-rule', '|',
            'preview', 'side-by-side', 'fullscreen', '|',
            'guide',
        ],
    });

    function showAlert(kind, message) {
        const safe = String(message);
        alertContainer.innerHTML = `
            <div class="alert alert-${kind} alert-dismissible" role="alert">
                <div>${safe}</div>
                <a class="btn-close" data-bs-dismiss="alert" aria-label="close"></a>
            </div>`;
    }

    function clearAlert() {
        alertContainer.innerHTML = '';
    }

    function getSelectedFormats() {
        return Array.from(document.querySelectorAll('.format-check:checked'))
            .map((el) => el.value);
    }

    async function loadTemplates() {
        try {
            const res = await fetch('/api/templates');
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }
            const data = await res.json();
            templateSelect.innerHTML = '';
            data.templates.forEach((tpl) => {
                const opt = document.createElement('option');
                opt.value = tpl.name;
                opt.textContent = tpl.name + (tpl.has_html ? '' : ' (incomplete)');
                opt.disabled = !tpl.has_html;
                if (tpl.name === 'ats_classic') {
                    opt.selected = true;
                }
                templateSelect.appendChild(opt);
            });
        } catch (err) {
            showAlert('danger', `Could not load templates: ${err.message}`);
        }
    }

    async function loadVersion() {
        try {
            const res = await fetch('/api/version');
            if (!res.ok) return;
            const data = await res.json();
            if (data && data.version) {
                versionBadge.textContent = `v${data.version}`;
            }
        } catch (_err) { /* non-fatal */ }
    }

    async function refreshPreview() {
        const markdown = editor.value();
        const template = templateSelect.value;
        if (!markdown.trim() || !template) {
            return;
        }
        try {
            const res = await fetch('/api/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ markdown, template }),
            });
            if (!res.ok) {
                const text = await res.text();
                showAlert('warning', `Preview failed (${res.status}): ${text}`);
                return;
            }
            const html = await res.text();
            previewFrame.srcdoc = html;
            clearAlert();
        } catch (err) {
            showAlert('danger', `Preview request error: ${err.message}`);
        }
    }

    function debounce(fn, ms) {
        let timer = null;
        return function (...args) {
            if (timer) clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), ms);
        };
    }

    const debouncedPreview = debounce(refreshPreview, 400);
    editor.codemirror.on('change', debouncedPreview);
    templateSelect.addEventListener('change', refreshPreview);

    convertBtn.addEventListener('click', async () => {
        const markdown = editor.value();
        const template = templateSelect.value;
        const formats = getSelectedFormats();
        if (!markdown.trim()) {
            showAlert('warning', 'Markdown content is empty.');
            return;
        }
        if (formats.length === 0) {
            showAlert('warning', 'Select at least one output format.');
            return;
        }
        convertBtn.disabled = true;
        convertBtn.innerHTML = '<i class="ti ti-loader"></i> Converting...';
        try {
            const res = await fetch('/api/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ markdown, template, formats }),
            });
            if (!res.ok) {
                const text = await res.text();
                throw new Error(`HTTP ${res.status} — ${text}`);
            }
            const blob = await res.blob();
            const ext = formats.length > 1 ? 'zip' : formats[0];
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `cv.${ext}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(a.href);
            clearAlert();
        } catch (err) {
            showAlert('danger', `Conversion failed: ${err.message}`);
        } finally {
            convertBtn.disabled = false;
            convertBtn.innerHTML = '<i class="ti ti-download"></i> Convert &amp; Download';
        }
    });

    loadVersion();
    loadTemplates().then(refreshPreview);
})();
