#!/usr/bin/env python3
"""
PDF Split Tool for FastMCP — Extract pages from PDF files and return text.
Designed to be used with via MCP protocol with LLMs frontends such as LM-Studio.
"""


from pathlib import Path
import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional, Union, Literal
from pypdf import PdfReader, PdfWriter
from fastmcp import FastMCP  # ← newer import style that expects Pydantic style annotation
from pydantic import BaseModel, Field, field_validator, ValidationInfo  # <-- for the Pydantic schema


# Configure a simple logger
logger = logging.getLogger("PDF-tool")
logging.basicConfig(level=logging.INFO)


class PDFSplitParams(BaseModel):
    """
    Pydantic model to validate and type-hint input parameters for PDF splitting operations.
    """
    file_path: str = Field(..., description="The path to the PDF file to split")
    start_page: int = Field(1, ge=1, description="The start page number (1-indexed)")
    end_page: int = Field(1, ge=1, description="The end page number (1-indexed)")
    save_pdf: bool = Field(False, description="Whether to save the new PDF file with the extracted pages")

    @field_validator('end_page')
    def end_page_must_be_greater_or_equal_to_start(cls, v: int, info: ValidationInfo) -> int:
        """Ensure end_page is not less than start_page
            @validator('end_page') → validator runs only on the end_page field.
            cls → The class itself (used in class methods).
            v → value being validated (end_page).
            values → dictionary of all other fields already validated (e.g., includes start_page).
        """
        start_page = info.data.get('start_page')  # access other fields in Pydantic-v2
        if start_page is not None and v < start_page:
            raise ValueError('end_page must be greater than or equal to start_page')
        return v

    @field_validator('file_path')
    def file_path_must_not_be_empty(cls, v: str) -> str:
        """Ensure file_path is not empty or just whitespace"""
        if not v.strip():
            raise ValueError('file_path cannot be empty or whitespace only')
        return v


mcp = FastMCP("PDF-tool")  # shown in LM Studio UI


@mcp.tool(description="Open and split a PDF file by page range (start_page, end_page).")
def open_and_split_pdf(file_path: str, start_page: int=1, end_page: int=1, save_pdf: bool=False) -> str:
    """
    Open and split a PDF file by a given start page and end page numbers and save the resulted new pdf.
    By default it extracts only the first page.

    Args:
        file_path (str): The path to the PDF file to split.
        start_page (int)=1: The start page number (1-indexed).
        end_page (int)=1: The end page number (1-indexed).
        save_pdf (bool)=False: whether to save the new PDF file with the extracted pages.
    Returns:
        Text content of the PDF file
    Example usage:
        open_and_split_pdf("/Users/danid/Downloads/report.pdf", 1, 3)
    """
    # Validate input parameters using the Pydantic model
    try:
        params = PDFSplitParams(
            file_path=file_path,
            start_page=start_page,
            end_page=end_page,
            save_pdf=save_pdf
        )
    except Exception as e:
        logger.error(f"Invalid input parameters: {str(e)}")
        return f"Error: Invalid input parameters - {str(e)}"

    logger.info(f"Splitting PDF '{params.file_path}' from page {params.start_page} to {params.end_page}...")
    try:
        if not os.path.exists(params.file_path):
            logger.error(f"Error: File '{params.file_path}' does not exist")
            return f"Error: File '{params.file_path}' does not exist"

        with PdfReader(params.file_path) as reader:
            total_pages = len(reader.pages)
            if params.end_page > total_pages:
                raise ValueError(
                    f"Requested page {params.end_page} exceeds the document length ({total_pages} pages)."
                )
            writer = PdfWriter()

            # Extract text from the page range for the new PDF and the returned text object
            text_parts = []
            for i in range(params.start_page - 1, params.end_page):
                writer.add_page(reader.pages[i])
                page = reader.pages[i]
                text_parts.append(f"--- Page {i + 1} ---\n{page.extract_text()}")

            if params.save_pdf:
                new_file_path = Path(params.file_path).parent/Path(Path(params.file_path).stem + "_pgs_" + str(params.start_page) + "-" + str(params.end_page) + Path(params.file_path).suffix)
                with open(new_file_path, "wb") as f:
                    writer.write(f)
                logger.info(f"Created new PDF: {new_file_path}")

            return f"Content from new PDF:\n\n" + "\n".join(text_parts)

    except Exception as e:
        logger.error(f"Error reading PDF '{params.file_path}': {str(e)}")
        return f"Error reading PDF '{params.file_path}': {str(e)}"


def main():
    """
    Launch the MCP server that hosts the 2 MCP functions defined above. FastMCP will pick an available port automatically. 
    LM-Studio will launch this file via the command you configured in *mcp.json*.
    """
    try:
        # Write to stderr immediately so LM Studio knows we're alive
        print("PDF-tool MCP server starting...", file=sys.stderr)

        # OPTIONAL: Add a tiny delay if you have heavy imports (e.g., pypdf)
        # This gives LM Studio time to connect before your server is ready
        # Remove this in production if you don't need it.
        time.sleep(0.5)

        # Start the server — this will block and wait for MCP messages
        print("PDF-tool MCP server ready to receive requests...", file=sys.stderr)
        mcp.run(transport="stdio")

    except Exception as e:
        print(f"PDF-tool crashed: {type(e).__name__}: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
