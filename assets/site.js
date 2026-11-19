(() => {
  'use strict';
  const root = document.documentElement;
  const toggle = document.getElementById('language-toggle');
  const messages = {
    en: { copy: 'Copy BibTeX', copied: 'Copied', failed: 'Select the citation text to copy.' },
    'zh-CN': { copy: '复制 BibTeX', copied: '已复制', failed: '请选中引用文本后复制。' }
  };
  function language() { return root.lang === 'zh-CN' ? 'zh-CN' : 'en'; }
  function setLanguage(value) {
    root.lang = value;
    toggle.textContent = value === 'en' ? '中文' : 'English';
    toggle.setAttribute('aria-label', value === 'en' ? '切换为中文' : 'Switch to English');
    const t = messages[value];
    document.querySelectorAll('.copy-button').forEach(button => { button.textContent = t.copy; });
    document.querySelectorAll('.copy-status').forEach(el => { el.textContent = ''; });
    document.querySelectorAll('img[data-alt-en]').forEach(img => { img.alt = value === 'en' ? img.dataset.altEn : img.dataset.altZh; });
    document.title = value === 'en' ? 'Yilong Fan | Tianjin University' : 'Yilong Fan | 天津大学';
    try { localStorage.setItem('academic-language', value); } catch { /* Storage is optional. */ }
  }
  toggle.addEventListener('click', () => setLanguage(language() === 'en' ? 'zh-CN' : 'en'));
  document.querySelectorAll('.bib-button').forEach(button => {
    button.addEventListener('click', () => {
      const panel = document.getElementById(button.getAttribute('aria-controls'));
      panel.hidden = !panel.hidden;
      button.setAttribute('aria-expanded', String(!panel.hidden));
    });
  });
  document.querySelectorAll('.copy-button').forEach(button => {
    button.addEventListener('click', async () => {
      const panel = button.closest('.bib-panel');
      const citation = panel.querySelector('pre');
      const feedback = panel.querySelector('.copy-status');
      const t = messages[language()];
      try {
        if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(citation.textContent);
        feedback.textContent = t.copied;
      } catch {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(citation);
        selection.removeAllRanges();
        selection.addRange(range);
        feedback.textContent = t.failed;
      }
    });
  });
  const figureDialog = document.getElementById('figure-dialog');
  if (figureDialog && typeof figureDialog.showModal === 'function') {
    document.querySelectorAll('.figure-link').forEach(link => {
      link.addEventListener('click', event => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
        event.preventDefault();
        const figure = link.querySelector('img');
        const enlarged = document.getElementById('figure-dialog-image');
        enlarged.src = link.href;
        enlarged.alt = figure.alt;
        document.getElementById('figure-dialog-title').textContent = link.dataset.figureTitle;
        document.getElementById('figure-dialog-caption').textContent = language() === 'en' ? link.dataset.captionEn : link.dataset.captionZh;
        figureDialog.showModal();
      });
    });
    document.getElementById('close-figure').addEventListener('click', () => figureDialog.close());
    figureDialog.addEventListener('click', event => {
      const rect = figureDialog.getBoundingClientRect();
      if (event.target === figureDialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) figureDialog.close();
    });
  }
  let preference = 'en';
  try { if (localStorage.getItem('academic-language') === 'zh-CN') preference = 'zh-CN'; } catch { /* Use English by default. */ }
  document.querySelectorAll('[data-enhanced]').forEach(el => { el.hidden = false; });
  setLanguage(preference);
})();
