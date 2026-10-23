"""PrintRush - PyScript version of script.js.
 
Runs in the browser through PyScript (Pyodide). It handles:
  1. the rotating promo messages in the top banner
  2. the pricing calculator
  3. the online order form
 
Planning prices come from the PrintRush feasibility study.
"""
import asyncio
import time
from html import escape
 
from pyscript import document, window, when # pyright: ignore[reportMissingImports]
 
 
# ---------- Helpers ----------
def peso(amount):
    return f"₱{amount:,.2f}"
 
 
def to_int(value, default=0):
    """Like JavaScript's parseInt(value) || 0."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default
 
 
# ---------- Rotating promo messages in the top banner ----------
PROMO_MESSAGES = [
    "Need to print modules fast? PrintRush offers affordable B&W printing for only ₱2.00 per page!",
    "Skip the long lines! Send your documents online before pickup.",
    "Short bond, A4, or long – we have your paper size covered.",
    "No online payment needed. Just pay in cash when you claim your prints!",
]
 
rotator = document.getElementById("promoRotator")
 
 
async def rotate_promos():
    index = 0
    while True:
        await asyncio.sleep(4)
        index = (index + 1) % len(PROMO_MESSAGES)
        rotator.style.opacity = "0"
        await asyncio.sleep(0.3)
        rotator.textContent = PROMO_MESSAGES[index]
        rotator.style.opacity = "0.9"
 
 
asyncio.ensure_future(rotate_promos())
 
 
# ---------- Pricing calculator ----------
service_select = document.getElementById("serviceType")
page_input = document.getElementById("pageCount")
paper_select = document.getElementById("paperSize")
total_el = document.getElementById("totalPrice")
calc_note = document.getElementById("calcNote")
 
 
def update_calculator():
    price = float(service_select.value)
    pages = max(0, to_int(page_input.value))
    total_el.textContent = peso(price * pages)
 
    option = paper_select.options.item(paper_select.selectedIndex)
    paper = option.text.split(" bond")[0].split(" (")[0]
    calc_note.textContent = f"{pages} page(s) × {peso(price)} on {paper} bond paper"
 
 
@when("input", "#serviceType, #pageCount, #paperSize")
def on_calculator_input(event):
    update_calculator()
 
 
update_calculator()
 
 
# ---------- Order form ----------
form = document.getElementById("orderForm")
order_service = document.getElementById("orderService")
order_pages = document.getElementById("orderPages")
order_total = document.getElementById("orderTotal")
file_upload = document.getElementById("fileUpload")
file_list = document.getElementById("fileList")
form_error = document.getElementById("formError")
confirmation = document.getElementById("confirmation")
 
 
def update_order_total():
    price = float(order_service.value)
    pages = max(0, to_int(order_pages.value))
    order_total.textContent = peso(price * pages)
 
 
@when("input", "#orderService, #orderPages")
def on_order_input(event):
    update_order_total()
 
 
update_order_total()
 
 
@when("change", "#fileUpload")
def on_files_change(event):
    file_list.innerHTML = ""
    files = file_upload.files
    for i in range(files.length):
        f = files.item(i)
        li = document.createElement("li")
        li.textContent = f"{f.name} ({f.size / 1024:.1f} KB)"
        file_list.appendChild(li)
 
 
def show_error(message):
    form_error.textContent = message
    form_error.hidden = False
 
 
@when("submit", "#orderForm")
def on_submit(event):
    event.preventDefault()
    form_error.hidden = True
 
    name = document.getElementById("custName").value.strip()
    contact = document.getElementById("custContact").value.strip()
    pages = to_int(order_pages.value)
    files = file_upload.files
 
    if not name or not contact:
        show_error("Please enter your name and contact number.")
        return
    if pages < 1:
        show_error("Please enter a valid number of pages.")
        return
    if files.length == 0:
        show_error("Please upload at least one file to print.")
        return
 
    payment = form.querySelector('input[name="payment"]:checked').value
    total = float(order_service.value) * pages
    ref = "PR-" + str(int(time.time() * 1000))[-6:]
 
    # NOTE: this demo has no server, so the files are not actually sent anywhere.
    confirmation.innerHTML = f"""
        <h3>✅ Order received, {escape(name)}!</h3>
        <p>We received <strong>{files.length} file(s)</strong> for quick processing.</p>
        <p>Order ref: <strong>{ref}</strong> · Estimated total: <strong>{peso(total)}</strong> · Payment: <strong>{payment}</strong></p>
        <p>Please show your order reference at pickup.</p>"""
    confirmation.hidden = False
    confirmation.scrollIntoView()
    window.alert(f"Thank you, {name}! Your files were received for quick processing.\nOrder ref: {ref}")
 
    form.reset()
    file_list.innerHTML = ""
    update_order_total()
 