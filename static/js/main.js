/* ============================================
   QUICKBITE — MAIN JS  (Django session cart)
   ============================================ */

// ── CART COUNT (fetched from server on load) ──
function refreshCartCount() {
  // We read the badge from the page; server sets it via context if needed.
  // For SPA-like updates we use the AJAX responses.
}

// ── ADD TO CART ──
function addToCart(itemId, name, price) {
  fetch('/cart/add/', {
    method:  'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken':  getCookie('csrftoken'),
    },
    body: JSON.stringify({ item_id: itemId }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      updateBadge(data.cart_count);
      showToast(`${name} added to cart! 🛒`, 'success');
      updateAddButton(itemId, true);
    } else if (data.error === 'different_restaurant') {
      if (confirm('Your cart has items from another restaurant. Clear cart and add this item?')) {
        clearCartThen(() => addToCart(itemId, name, price));
      }
    } else if (data.error === 'login_required') {
      window.location.href = '/login/?next=' + window.location.pathname;
    } else {
      showToast(data.message || 'Could not add item', 'error');
    }
  })
  .catch(() => showToast('Network error', 'error'));
}

// ── CHANGE QUANTITY ──
function changeQty(itemId, delta) {
  fetch('/cart/update/', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
    body: JSON.stringify({ item_id: itemId, delta }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      updateBadge(data.cart_count);
      // Refresh qty display on page if element exists
      const qtyEl = document.getElementById(`qty-${itemId}`);
      if (qtyEl) {
        const newQty = parseInt(qtyEl.textContent) + delta;
        if (newQty <= 0) {
          qtyEl.closest('.cart-item')?.remove();
          updateAddButton(itemId, false);
        } else {
          qtyEl.textContent = newQty;
        }
      }
      // Update total display
      const totalEl = document.getElementById('cartTotal');
      if (totalEl && data.total !== undefined) {
        totalEl.textContent = '₹' + Math.round(data.total);
      }
    }
  });
}

// ── CLEAR CART ──
function clearCartThen(callback) {
  fetch('/cart/clear/', {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') },
  })
  .then(r => r.json())
  .then(() => {
    updateBadge(0);
    if (callback) callback();
  });
}

// ── BADGE ──
function updateBadge(count) {
  document.querySelectorAll('#cart-count, .cart-badge').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
}

// ── ADD BUTTON STATE ──
function updateAddButton(itemId, added) {
  const btn = document.querySelector(`[data-item-id="${itemId}"]`);
  if (!btn) return;
  if (added) {
    btn.innerHTML = `
      <div class="qty-control">
        <button class="qty-btn" onclick="changeQty(${itemId},-1);event.stopPropagation()">−</button>
        <span class="qty-num" id="qty-${itemId}">1</span>
        <button class="qty-btn" onclick="changeQty(${itemId},1);event.stopPropagation()">+</button>
      </div>`;
    btn.style.cssText = 'border:none;padding:0;background:transparent;';
  } else {
    btn.innerHTML = '+ Add';
    btn.style.cssText = '';
  }
}

// ── CART SIDEBAR ──
function toggleCart() {
  const sidebar = document.getElementById('cartSidebar');
  const overlay = document.getElementById('cartOverlay');
  if (!sidebar) return;
  const isOpen = sidebar.classList.toggle('open');
  overlay.classList.toggle('show', isOpen);
  document.body.style.overflow = isOpen ? 'hidden' : '';
  // If opening, reload cart content from server
  if (isOpen) loadCartSidebar();
}

function loadCartSidebar() {
  fetch('/cart/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(r => r.json())
    .then(data => {
      const body   = document.getElementById('cartBody');
      const footer = document.getElementById('cartFooter');
      const totalEl = document.getElementById('cartTotal');
      if (!body) return;

      if (!data.items || data.items.length === 0) {
        body.innerHTML = `
          <div class="empty-state">
            <div class="empty-emoji">🛒</div>
            <h3>Your cart is empty</h3>
            <p>Add items from a restaurant to get started</p>
          </div>`;
        if (footer) footer.style.display = 'none';
        return;
      }

      let html = '';
      data.items.forEach(item => {
        html += `
          <div class="cart-item" style="display:flex;align-items:center;gap:12px;padding:14px 16px;border-bottom:1px solid var(--border);">
            <div style="flex:1;">
              <div style="font-size:13px;font-weight:600;display:flex;align-items:center;gap:6px;">
                <span style="width:10px;height:10px;border-radius:50%;background:${item.is_veg ? '#1ba672' : '#e74c3c'};display:inline-block;flex-shrink:0;"></span>
                ${item.name}
              </div>
              <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">₹${item.price} each</div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <button onclick="changeQty(${item.id},-1)" style="width:26px;height:26px;border-radius:50%;border:1.5px solid var(--primary);background:#fff;color:var(--primary);font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-weight:700;">−</button>
              <span id="qty-${item.id}" style="font-size:14px;font-weight:700;min-width:18px;text-align:center;">${item.quantity}</span>
              <button onclick="changeQty(${item.id},1)" style="width:26px;height:26px;border-radius:50%;background:var(--primary);border:none;color:#fff;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-weight:700;">+</button>
            </div>
            <div style="font-size:13px;font-weight:700;min-width:48px;text-align:right;">₹${Math.round(item.total)}</div>
          </div>`;
      });

      // Bill summary
      html += `
        <div style="padding:14px 16px;background:var(--bg);">
          <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text-muted);margin-bottom:6px;">
            <span>Subtotal</span><span>₹${Math.round(data.subtotal)}</span>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text-muted);margin-bottom:6px;">
            <span>Delivery</span>
            <span style="color:${data.delivery_fee === 0 ? 'var(--success)' : 'inherit'}">${data.delivery_fee === 0 ? 'FREE' : '₹' + data.delivery_fee}</span>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text-muted);">
            <span>Platform fee</span><span>₹5</span>
          </div>
        </div>`;

      body.innerHTML = html;
      if (footer) footer.style.display = 'block';
      if (totalEl) totalEl.textContent = '₹' + Math.round(data.total);
      updateBadge(data.count);
    })
    .catch(() => {});
}

// ── TOAST ──
function showToast(msg, type = '') {
  let toast = document.getElementById('js-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'js-toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.className = `toast ${type}`;
  requestAnimationFrame(() => {
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2800);
  });
}

// ── CSRF ──
function getCookie(name) {
  const val = `; ${document.cookie}`;
  const parts = val.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

// ── LIVE SEARCH (menu page) ──
function liveSearch(input) {
  const q = input.value.toLowerCase();
  document.querySelectorAll('.menu-item-wrapper').forEach(card => {
    const name = card.querySelector('.item-name')?.textContent.toLowerCase() || '';
    card.style.display = name.includes(q) ? '' : 'none';
  });
}

// ── AUTO-HIDE DJANGO MESSAGES ──
document.addEventListener('DOMContentLoaded', () => {
  const djangoToast = document.getElementById('django-toast');
  if (djangoToast) {
    setTimeout(() => djangoToast.classList.remove('show'), 3000);
  }
});

// ── CONFIRM DELETE ──
function confirmDelete(form) {
  if (confirm('Are you sure you want to delete this?')) form.submit();
}


// ═══ CUSTOM MODAL ═══
function showModal(config) {
  const modal = document.getElementById('customModal');
  document.getElementById('modalIcon').textContent  = config.icon  || '⚠️';
  document.getElementById('modalTitle').textContent = config.title || 'Are you sure?';
  document.getElementById('modalMsg').textContent   = config.msg   || '';
  const btn = document.getElementById('modalConfirmBtn');
  btn.textContent       = config.btnText  || 'Confirm';
  btn.style.background  = config.btnColor || '#fc8019';
  btn.onclick           = () => { closeModal(); config.onConfirm(); };
  modal.style.display   = 'flex';
}

function closeModal() {
  document.getElementById('customModal').style.display = 'none';
}

// ═══ CUSTOM TOAST ═══
function showToast(msg, type = 'success') {
  const toast = document.getElementById('customToast');
  const colors = { success: '#1ba672', error: '#e74c3c', info: '#1565c0', warning: '#ff9800' };
  toast.textContent      = msg;
  toast.style.background = colors[type] || colors.success;
  toast.style.display    = 'block';
  setTimeout(() => { toast.style.display = 'none'; }, 3000);
}

// ═══ OVERRIDE confirmDelete ═══
function confirmDelete(form) {
  showModal({
    icon: '🗑️',
    title: 'Delete this?',
    msg: 'This action cannot be undone.',
    btnText: 'Yes, Delete',
    btnColor: '#e74c3c',
    onConfirm: () => form.submit()
  });
}