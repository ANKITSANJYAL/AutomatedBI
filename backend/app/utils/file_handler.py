import os
import shutil
from pathlib import Path
import pandas as pd
from typing import Optional, Union
import structlog

logger = structlog.get_logger(__name__)


class FileHandler:
    """Handle file operations for uploaded datasets"""
    
    def __init__(self, upload_folder: str):
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file, filename: str) -> str:
        """Save uploaded file to the upload folder"""
        try:
            file_path = self.upload_folder / filename
            file.save(str(file_path))
            
            logger.info("File saved successfully", filename=filename, path=str(file_path))
            return str(file_path)
            
        except Exception as e:
            logger.error("Error saving file", filename=filename, error=str(e))
            raise
    
    def read_dataset(self, file_path: str) -> pd.DataFrame:
        """Read dataset from file into pandas DataFrame"""
        try:
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.csv':
                # Try different encodings and separators
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # If all encodings fail, try with error handling
                    df = pd.read_csv(file_path, encoding='utf-8', errors='replace')
            
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Basic data cleaning
            df = self._clean_dataframe(df)
            
            logger.info(
                "Dataset loaded successfully", 
                filename=file_path.name,
                rows=len(df),
                columns=len(df.columns)
            )
            
            return df
            
        except Exception as e:
            logger.error("Error reading dataset", file_path=str(file_path), error=str(e))
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform basic data cleaning"""
        try:
            # Remove completely empty rows and columns
            df = df.dropna(how='all')
            df = df.dropna(axis=1, how='all')
            
            # Clean column names
            df.columns = df.columns.astype(str)
            df.columns = df.columns.str.strip()
            
            # Remove duplicate column names
            df.columns = self._make_unique_columns(df.columns.tolist())
            
            # Try to infer and convert data types
            df = self._infer_dtypes(df)
            
            return df
            
        except Exception as e:
            logger.error("Error cleaning dataframe", error=str(e))
            return df  # Return original if cleaning fails
    
    def _make_unique_columns(self, columns: list) -> list:
        """Ensure column names are unique"""
        seen = set()
        result = []
        
        for col in columns:
            original_col = col
            counter = 1
            
            while col in seen:
                col = f"{original_col}_{counter}"
                counter += 1
            
            seen.add(col)
            result.append(col)
        
        return result
    
    def _infer_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Infer and convert appropriate data types"""
        try:
            for col in df.columns:
                # Skip if column is already numeric
                if df[col].dtype in ['int64', 'float64']:
                    continue
                
                # Try to convert to numeric
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                if not numeric_col.isna().all():
                    # If conversion is successful for most values, use it
                    non_null_original = df[col].count()
                    non_null_converted = numeric_col.count()
                    
                    if non_null_converted / non_null_original > 0.8:  # 80% conversion success
                        df[col] = numeric_col
                        continue
                
                # Try to convert to datetime
                try:
                    datetime_col = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    if not datetime_col.isna().all():
                        non_null_original = df[col].count()
                        non_null_converted = datetime_col.count()
                        
                        if non_null_converted / non_null_original > 0.8:  # 80% conversion success
                            df[col] = datetime_col
                            continue
                except:
                    pass
            
            return df
            
        except Exception as e:
            logger.error("Error inferring data types", error=str(e))
            return df
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from filesystem"""
        try:
            file_path = Path(file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info("File deleted successfully", file_path=str(file_path))
                return True
            else:
                logger.warning("File not found for deletion", file_path=str(file_path))
                return False
                
        except Exception as e:
            logger.error("Error deleting file", file_path=str(file_path), error=str(e))
            return False
    
    def cleanup_old_files(self, days: int = 7) -> int:
        """Clean up files older than specified days"""
        try:
            import time
            current_time = time.time()
            deleted_count = 0
            
            for file_path in self.upload_folder.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (days * 24 * 60 * 60):  # Convert days to seconds
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info("File cleanup completed", deleted_files=deleted_count, days=days)
            return deleted_count
            
        except Exception as e:
            logger.error("Error during file cleanup", error=str(e))
            return 0
