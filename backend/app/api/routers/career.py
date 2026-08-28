import os

from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.services.career.career_analysis_service import (
    career_analysis_service,
)
from app.services.resume_service import (
    resume_service,
)


router = APIRouter(
    prefix="/career",
    tags=["Career Intelligence"],
)


@router.post("/analyze")
async def analyze_career(
    file: UploadFile = File(...),
):
    """
    Upload a resume and run the complete
    CareerOS career intelligence pipeline.

    Automatically analyzes:

    - Resume
    - LinkedIn
    - GitHub
    - LeetCode
    - Unified cross-source evidence
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in {
        ".pdf",
        ".docx",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF and DOCX "
                "resumes are supported."
            ),
        )

    # ==================================================
    # UPLOAD
    # ==================================================

    try:
        upload_result = (
            await resume_service.upload_resume(
                file
            )
        )

    except HTTPException:
        raise

    except Exception as exc:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Failed to upload resume.",
        ) from exc

    resume_id = upload_result.file_id

    pdf_path = os.path.join(
        resume_service.upload_dir,
        f"{resume_id}.pdf",
    )

    docx_path = os.path.join(
        resume_service.upload_dir,
        f"{resume_id}.docx",
    )

    if os.path.exists(pdf_path):
        resume_path = pdf_path

    elif os.path.exists(docx_path):
        resume_path = docx_path

    else:
        raise HTTPException(
            status_code=500,
            detail=(
                "Resume was uploaded but "
                "the stored file could not "
                "be located."
            ),
        )

    # ==================================================
    # FULL CAREER INTELLIGENCE
    #
    # IMPORTANT:
    # career_analysis_service.analyze() is synchronous
    # and performs blocking network/API work.
    #
    # Run it in a worker thread so the FastAPI event
    # loop remains responsive to Render health checks.
    # ==================================================

    try:
        result = await run_in_threadpool(
            career_analysis_service.analyze,
            resume_path,
        )

    except Exception as exc:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Career intelligence "
                f"pipeline failed: {exc}"
            ),
        ) from exc

    # ==================================================
    # RESPONSE
    # ==================================================

    return {
        "success": True,

        "file": {
            "file_id": resume_id,

            "filename": (
                upload_result.filename
            ),

            "original_filename": (
                upload_result.original_filename
            ),
        },

        "analysis": result,
    }