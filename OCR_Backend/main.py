"""
main.py
--------
Standalone FastAPI entry point so this OCR module can be run and tested
on its own, independent of the rest of the team's project.

When this module is later merged into the main project's FastAPI app,
the only thing another teammate needs to do is:

    from OCR_Backend.ocr_routes import router as ocr_router
    app.include_router(ocr_router)

...inside the main app's entry file. This file just does that for now,
on its own, so the OCR module can run standalone.
"""

from fastapi import FastAPI

from ocr_routes import router as ocr_router

app = FastAPI(
    title="OCR / Document Intelligence Module",
    description="Document upload + OCR text extraction for the "
                 "Voice Based Government Scheme Assistant project.",
)

app.include_router(ocr_router)


@app.get("/")
def health_check():
    """Simple health-check endpoint - useful to confirm the server is up."""
    return {"status": "ok", "module": "OCR / Document Intelligence"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
