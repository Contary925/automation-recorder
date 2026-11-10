import os

from playwright.sync_api import sync_playwright

PATH_TO_VIDEO_FOLDER = "./video"


CURSOR_SCRIPT = """
(() => {
    const initCursor = () => {
    const style = document.createElement("style");
    style.textContent = `
        html, body {
            cursor: none !important;
        }

        #automation-cursor-highlight {
            position: fixed;
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: rgba(255, 220, 0, 0.25);
            pointer-events: none;
            z-index: 2147483646;
            transform: translate(-50%, -50%);
        }

        #automation-cursor {
            position: fixed;
            width: 32px;
            height: 32px;
            pointer-events: none;
            z-index: 2147483647;
        }

        .automation-click-ripple {
            position: fixed;
            width: 8px;
            height: 8px;
            border: 2px solid rgba(255, 220, 0, 0.9);
            border-radius: 50%;
            pointer-events: none;
            z-index: 2147483645;
            transform: translate(-50%, -50%);
            animation: automation-ripple 0.5s ease-out forwards;
        }

        @keyframes automation-ripple {
            from {
                width: 8px;
                height: 8px;
                opacity: 1;
            }
            to {
                width: 64px;
                height: 64px;
                opacity: 0;
            }
        }
    `;
    document.documentElement.appendChild(style);

    const highlight = document.createElement("div");
    highlight.id = "automation-cursor-highlight";

    const cursor = document.createElement("div");
    cursor.id = "automation-cursor";
    cursor.innerHTML = `
        <svg width="32" height="32" viewBox="0 0 32 32">
            <path
                d="M 3 2 L 3 27 L 10 20 L 15 30 L 20 27 L 15 17 L 25 17 Z"
                fill="white"
                stroke="black"
                stroke-width="1.5"
                stroke-linejoin="round"
            />
        </svg>
    `;

    document.documentElement.appendChild(highlight);
    document.documentElement.appendChild(cursor);

    document.addEventListener("mousemove", (event) => {
        const x = event.clientX;
        const y = event.clientY;

        highlight.style.left = `${x}px`;
        highlight.style.top = `${y}px`;

        cursor.style.left = `${x}px`;
        cursor.style.top = `${y}px`;
    }, true);

    document.addEventListener("click", (event) => {
        const ripple = document.createElement("div");
        ripple.className = "automation-click-ripple";
        ripple.style.left = `${event.clientX}px`;
        ripple.style.top = `${event.clientY}px`;

        document.documentElement.appendChild(ripple);
        ripple.addEventListener("animationend", () => ripple.remove());
    }, true);
    };

    if (document.documentElement) {
        initCursor();
    } else {
        document.addEventListener("DOMContentLoaded", initCursor, { once: true });
    }
})();
"""


def _move_mouse_smoothly(page, x, y):
    """Move the mouse to the target point with intermediate steps."""
    page.mouse.move(x, y, steps=30)
    page.wait_for_timeout(100)


def _click_locator(page, locator):
    """Move the mouse to the center of an element and click it."""
    locator.wait_for(state="visible", timeout=30000)

    bounds = locator.bounding_box()
    if bounds is None:
        raise RuntimeError("Could not determine element position")

    x = bounds["x"] + bounds["width"] / 2
    y = bounds["y"] + bounds["height"] / 2

    _move_mouse_smoothly(page, x, y)
    page.mouse.click(x, y)


def ShowCallout(page, text, bgColor="yellow", textColor="black", fade=True):
    """Display a short notification on the page."""
    page.evaluate(
        """({text, bgColor, textColor, fade}) => {
            const box = document.createElement("div");

            box.textContent = text;
            Object.assign(box.style, {
                position: "fixed",
                top: "24px",
                left: "50%",
                transform: "translateX(-50%)",
                padding: "14px 22px",
                background: bgColor,
                color: textColor,
                fontSize: "16pt",
                fontFamily: "Arial, sans-serif",
                border: "2px solid black",
                borderRadius: "6px",
                zIndex: "2147483647",
                opacity: fade ? "0" : "1",
                transition: "opacity 2s ease",
            });

            document.documentElement.appendChild(box);

            if (fade) {
                requestAnimationFrame(() => {
                    box.style.opacity = "1";
                });

                setTimeout(() => {
                    box.style.opacity = "0";
                    setTimeout(() => box.remove(), 2000);
                }, 4000);
            }
        }""",
        {
            "text": text,
            "bgColor": bgColor,
            "textColor": textColor,
            "fade": fade,
        },
    )


def _make_video_filename(company_name):
    """Create a safe video filename from the company name."""
    invalid_chars = '<>:"/\\|?*'

    filename = "".join(
        "_" if char in invalid_chars or ord(char) < 32 else char
        for char in company_name
    ).strip().rstrip(".")

    if not filename:
        filename = "recording"

    return filename + ".webm"


def CaptureVideo_Magento(
    url,
    company_name,
    language,
    country,
    postcode,
    city,
    street,
    house_no,
):
    page = None
    os.makedirs(PATH_TO_VIDEO_FOLDER, exist_ok=True)
    output_folder = os.path.abspath(PATH_TO_VIDEO_FOLDER)

    browser = None
    context = None
    recording = None
    temporary_path = None
    failed = False

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=False)

            locale = _get_browser_locale(language, country)

            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                record_video_dir=output_folder,
                record_video_size={"width": 1280, "height": 720},
                locale=locale,
            )

            context.add_init_script(CURSOR_SCRIPT)

            page = context.new_page()
            recording = page.video

            page.set_content(f"""
                <html>
                    <body style="
                        margin: 0;
                        height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: #202b3a;
                        color: white;
                        font-family: Arial, sans-serif;
                    ">
                        <div style="text-align: center;">
                            <h1>{company_name}</h1>
                            <p>Searching for Magento developers in {city}</p>
                        </div>
                    </body>
                </html>
            """)

            page.wait_for_timeout(1500)

            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            search_box = page.locator(
                'input[name="q"]:visible, textarea[name="q"]:visible'
            ).first

            search_box.wait_for(state="visible", timeout=30000)

            ShowCallout(
                page,
                f"{company_name}: searching for Magento developers in {city}",
            )

            search_box = page.locator(
                'input[name="q"]:visible, textarea[name="q"]:visible'
            ).first
            search_box.evaluate("""
                element => {
                    const form = element.closest("form");

                    for (const [name, value] of [
                        ["setlang", "en"],
                        ["mkt", "en-US"]
                    ]) {
                        let input = form.querySelector(`input[name="${name}"]`);

                        if (!input) {
                            input = document.createElement("input");
                            input.type = "hidden";
                            input.name = name;
                            form.appendChild(input);
                        }

                        input.value = value;
                    }
                }
            """)
            _click_locator(page, search_box)

            query = f"Magento developer in {city}"
            search_box.fill("")
            search_box.type(query, delay=110)
            search_box.press("Enter")
            page.wait_for_url("**/search?**", timeout=30000)
            page.wait_for_load_state("domcontentloaded")

            first_result = page.locator(
                "#b_results li.b_algo h2 a:visible"
            ).first

            first_result.wait_for(state="visible", timeout=30000)
            # Открываем ссылку в текущей вкладке.
            first_result.evaluate(
                "(element) => element.setAttribute('target', '_self')"
            )

            _click_locator(page, first_result)

            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            address = ", ".join(
                part.strip()
                for part in (street, house_no, postcode, city, country)
                if part and part.strip()
            )

            ShowCallout(
                page,
                f"{company_name} | {address}",
            )

            page.wait_for_timeout(5000)

        except Exception as error:
            print(f"Recording failed for {company_name}: {error}")
            failed = True

            if page is not None:
                try:
                    print(f"Current URL: {page.url}")
                    print(f"Page title: {page.title()}")
                    print(
                        f"Search results found: "
                        f"{page.locator('#b_results li.b_algo').count()}"
                    )

                    debug_name = _make_video_filename(company_name)
                    debug_path = os.path.join(
                        output_folder,
                        f"debug_{debug_name}.png",
                    )
                    page.screenshot(path=debug_path, full_page=True)
                    print(f"Debug screenshot: {debug_path}")

                    print("Page text:")
                    print(page.locator("body").inner_text()[:1500])

                except Exception as debug_error:
                    print(f"Could not collect diagnostics: {debug_error}")

        finally:
            if context is not None:
                try:
                    context.close()
                    if recording is not None:
                        temporary_path = recording.path()
                except Exception as error:
                    print(f"Could not finalize video: {error}")
                    failed = True

            if browser is not None:
                try:
                    browser.close()
                except Exception:
                    pass

    if temporary_path is None:
        return None

    if failed:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)
        return None

    filename = _make_video_filename(company_name)
    final_path = os.path.join(output_folder, filename)

    base, extension = os.path.splitext(final_path)
    counter = 2

    while os.path.exists(final_path):
        final_path = f"{base}_{counter}{extension}"
        counter += 1

    try:
        os.replace(temporary_path, final_path)
        return final_path
    except Exception as error:
        print(f"Could not save video for {company_name}: {error}")
        return None

def _get_browser_locale(language, country):
    languages = {
        "english": "en",
        "russian": "ru",
        "belarusian": "be",
    }

    countries = {
        "belarus": "BY",
        "russia": "RU",
        "united states": "US",
        "usa": "US",
        "united kingdom": "GB",
        "uk": "GB",
    }

    lang = languages.get(language.strip().lower(), language.strip().lower())
    country_code = countries.get(
        country.strip().lower(),
        country.strip().upper(),
    )

    if len(lang) < 2 or len(country_code) != 2:
        return "en-US"

    return f"{lang}-{country_code}"