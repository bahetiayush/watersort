import base64
import json
import re
import time
import os
import collections
from typing import Dict, Any, List, Optional, Tuple

import requests
from dotenv import load_dotenv

from tube_setup import COLORS_WITH_HEX

load_dotenv()

# --- LLM API Configuration ---
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_KEY")

# Basic check for keys on startup
if not ANTHROPIC_API_KEY:
    print("Warning: ANTHROPIC_API_KEY environment variable not set. Anthropic provider will not work.")
if not OPENROUTER_API_KEY:
    print("Warning: OPEN_ROUTER_KEY environment variable not set. OpenRouter provider will not work.")


class ImageAnalyzer:
    """Handles image analysis using LLM APIs to extract tube colors."""

    @staticmethod
    def analyze_image_with_llm(image_data: str, image_type: str, provider: str = "anthropic", imbalance_info: str = None, retry_count: int = 0) -> Dict[str, Any]:
        """Sends image to the specified LLM API provider, handles response, and returns tube colors."""

        if provider == "anthropic" and not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set, cannot use 'anthropic' provider.")
        if provider == "openrouter" and not OPENROUTER_API_KEY:
             raise ValueError("OPENROUTER_API_KEY environment variable not set, cannot use 'openrouter' provider.")

        total_colors_str = str(COLORS_WITH_HEX)
        example_json = {
            "tubes": [
                {"name": "Tube1", "colors": ["BROWN", "LIGHT_GREEN", "BLUE", "GREY"]},
                {"name": "Tube2", "colors": ["GREEN", "RED", "RED", "GREEN"]},
            ]
        }
        example_json_str = json.dumps(example_json, indent=2)

        # --- Prepare Request based on Provider ---
        api_url = ""
        headers = {}
        payload = {}

        # Common message content (used by both)
        prompt_text = f"""I want the tube colours from this image in a JSON format suitable for Python processing. Your response must be only the JSON object, without any surrounding text or explanations.

Analyze all tubes shown in the image. The final JSON must represent the colors in *every* tube accurately.

**Output Requirements & Constraints:**
*   The output must be a JSON object with a single key "tubes" containing an array of tube objects.
*   Each tube object must have a "name" (e.g., "Tube1", "Tube2") and a "colors" array.
*   The "colors" array must contain exactly 4 elements, representing colors from bottom to top. Use the string "None" for empty slots.
*   The last two tubes in the image must be represented as completely empty: `"colors": ["None", "None", "None", "None"]`.
*   All other tubes must be full (4 non-"None" color entries). Pay attention to blended colors of the same type.
*   **Crucially:** Across the entire final JSON output, each valid color name must appear exactly 4 times in total.
*   Valid color names (match approximately based on hex codes): {total_colors_str}

**Validation Step (Internal):** Before generating the JSON, double-check your analysis to ensure all constraints above are met, especially the total count for each color across all tubes.
"""

        # Add imbalance information if this is a retry
        if imbalance_info and retry_count > 0:
            prompt_text += f"""
**IMPORTANT CORRECTION NEEDED:** Your previous analysis had color count issues:
{imbalance_info}

Please carefully reanalyze the image and ensure each color appears exactly 4 times total across all tubes.
"""

        prompt_text += f"""
**Example JSON Structure:**
{example_json_str}
"""
        message_content = [
            {"type": "text", "text": prompt_text},
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_type,
                    "data": image_data,
                },
            },
        ]

        if provider == "anthropic":
            api_url = ANTHROPIC_API_URL
            headers = {
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
            }
            payload = {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1000,
                "system": "You are a JSON-only response bot. Never include explanations or text outside of valid JSON structures.",
                "messages": [{"role": "user", "content": message_content}],
            }
        elif provider == "openrouter":
            api_url = OPENROUTER_API_URL
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                # OpenRouter often requires these headers
                "HTTP-Referer": "http://localhost:8000", # Adjust if your app URL is different
                "X-Title": "WaterSort Solver", # Can be your app's name
            }
            # OpenRouter uses OpenAI's chat completion format
            payload = {
                "model": "google/gemini-2.5-pro-exp-03-25:free",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": message_content}],
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        # --- Send Request, Process Response, Validate, and Retry ---
        max_attempts = 3
        last_error = None

        for attempt in range(max_attempts):
            print(f"Attempt {attempt + 1}/{max_attempts} to analyze image with {provider}...")
            try:
                # Simplified error handling - one big try/except block
                # Make the API request
                response = requests.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                response_data = response.json()

                # Extract result text based on provider's response structure
                result_text = ""
                if provider == "anthropic":
                    result_text = response_data.get("content", [{}])[0].get("text", "")
                elif provider == "openrouter":
                    # OpenAI/OpenRouter format
                    result_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

                if not result_text:
                    raise Exception("Could not extract result text from LLM response")

                # Extract JSON from the response
                extracted_data = ImageAnalyzer.extract_json(result_text)
                if "error" in extracted_data:
                    raise Exception(f"JSON extraction failed: {extracted_data.get('error')}")

                # Basic validation - just make sure 'tubes' exists
                if "tubes" not in extracted_data or not isinstance(extracted_data["tubes"], list):
                    raise Exception("'tubes' key missing or not a list in the response")

                # Optional validation - log warnings but don't fail
                try:
                    ImageAnalyzer.validate_tube_colors(extracted_data["tubes"])
                except Exception as validation_error:
                    # Just log the validation error but continue with the data
                    print(f"Warning: Color validation failed but proceeding: {str(validation_error)}")
                
                # Success - return the data even if validation had warnings
                print(f"Attempt {attempt + 1} successful.")
                return extracted_data

            except Exception as e:
                # Catch ALL exceptions in one handler
                last_error = str(e)
                print(f"Attempt {attempt + 1} failed: {last_error}")
                time.sleep(1)  # Wait before retrying
                continue  # Go to next attempt

        # If all attempts failed
        final_error_message = f"Failed to get valid tube data from {provider} after {max_attempts} attempts."
        if last_error:
            final_error_message += f" Last error: {last_error}"
        return {"error": final_error_message}
    
    @staticmethod
    def validate_tube_colors(tubes_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validates color counts and returns validation result."""
        color_counts = collections.Counter()
        valid_color_names = set(COLORS_WITH_HEX.keys())
        imbalanced_colors = {}
        
        # Count all colors
        for tube in tubes_data:
            if "colors" not in tube or not isinstance(tube["colors"], list):
                return {"valid": False, "error": f"Invalid 'colors' format in tube {tube.get('name', 'N/A')}"}
                
            for color in tube["colors"]:
                if color is not None and color != "None" and isinstance(color, str):
                    upper_color = color.upper()  # Normalize case
                    if upper_color in valid_color_names:
                        color_counts[upper_color] += 1
                    else:
                        return {"valid": False, "error": f"Unrecognized color '{color}' found in tube {tube.get('name', 'N/A')}"}

        # Check if all colors have exactly 4 instances
        expected_count = 4
        for color_name in valid_color_names:
            if color_name != "NONE" and color_counts[color_name] != expected_count:
                imbalanced_colors[color_name] = {
                    "count": color_counts[color_name],
                    "diff": color_counts[color_name] - expected_count
                }
        
        # Print a single, clear summary of imbalanced colors
        if imbalanced_colors:
            print("Color validation failed - Imbalanced colors:")
            for color, info in imbalanced_colors.items():
                if info["diff"] > 0:
                    print(f"  - {color}: has {info['count']} instances (should have 4, {info['diff']} too many)")
                else:
                    print(f"  - {color}: has {info['count']} instances (should have 4, {abs(info['diff'])} too few)")
            
            return {
                "valid": False,
                "imbalanced_colors": imbalanced_colors,
                "color_counts": dict(color_counts)
            }
        
        print("Color validation passed - All colors have exactly 4 instances")
        return {"valid": True, "color_counts": dict(color_counts)}
        
    @staticmethod
    def balance_tube_colors(tubes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Balances the colors in the tubes to ensure each color appears exactly 4 times.
        Prioritizes changes in later tubes and processes them in reverse order.
        """
        # Make a deep copy to avoid modifying the original data
        import copy
        balanced_tubes = copy.deepcopy(tubes_data)
        
        # Count occurrences of each color
        color_counts = collections.Counter()
        for tube in balanced_tubes:
            for color in tube["colors"]:
                if color is not None and color != "None" and isinstance(color, str):
                    color_counts[color] += 1
        
        # Identify excess and deficit colors
        excess_colors = {color: count for color, count in color_counts.items() if count > 4}
        deficit_colors = {color: 4 - count for color, count in color_counts.items() 
                         if count < 4 and color != "None" and color is not None}
        
        # If balanced, return the original data
        if not excess_colors and not deficit_colors:
            return balanced_tubes
        
        print(f"Balancing colors - Excess: {excess_colors}, Deficit: {deficit_colors}")
        
        # Create a map of replacements needed
        replacements_needed = []
        for excess_color, excess_count in excess_colors.items():
            for deficit_color, deficit_count in list(deficit_colors.items()):
                replace_count = min(excess_count, deficit_count)
                if replace_count > 0:
                    replacements_needed.append((excess_color, deficit_color, replace_count))
                    excess_colors[excess_color] -= replace_count
                    deficit_colors[deficit_color] -= replace_count
                    if deficit_colors[deficit_color] == 0:
                        del deficit_colors[deficit_color]
                    if excess_colors[excess_color] == 0:
                        break
        
        print(f"Replacements needed: {replacements_needed}")
        
        # Apply replacements - process tubes in reverse order
        for excess_color, deficit_color, count in replacements_needed:
            replacements_made = 0
            
            # First try tubes with mixed colors (prioritize these for replacement)
            # Process tubes in reverse order (last to first)
            for tube_index in range(len(balanced_tubes) - 1, -1, -1):
                tube = balanced_tubes[tube_index]
                if replacements_made >= count:
                    break
                
                # Check if tube has mixed colors
                tube_colors = set(tube["colors"]) - {None, "None"}
                if len(tube_colors) > 1:
                    # Process slots in reverse order (top to bottom)
                    for i in range(len(tube["colors"]) - 1, -1, -1):
                        if tube["colors"][i] == excess_color and replacements_made < count:
                            tube["colors"][i] = deficit_color
                            replacements_made += 1
                            print(f"Replaced {excess_color} with {deficit_color} in mixed tube {tube['name']} (position {i})")
            
            # If still need replacements, try any tube (still in reverse order)
            if replacements_made < count:
                for tube_index in range(len(balanced_tubes) - 1, -1, -1):
                    tube = balanced_tubes[tube_index]
                    if replacements_made >= count:
                        break
                    # Process slots in reverse order
                    for i in range(len(tube["colors"]) - 1, -1, -1):
                        if tube["colors"][i] == excess_color and replacements_made < count:
                            tube["colors"][i] = deficit_color
                            replacements_made += 1
                            print(f"Replaced {excess_color} with {deficit_color} in tube {tube['name']} (position {i})")
        
        # Verify the balance (just a single print for the final result)
        final_counts = collections.Counter()
        for tube in balanced_tubes:
            for color in tube["colors"]:
                if color is not None and color != "None" and isinstance(color, str):
                    final_counts[color] += 1
        
        imbalanced_after = False
        for color, count in final_counts.items():
            if count != 4:
                if not imbalanced_after:
                    print("Warning: Some colors are still imbalanced after balancing:")
                    imbalanced_after = True
                print(f"  - {color}: has {count} instances (expected 4)")
        
        if not imbalanced_after:
            print("Color balancing successful - All colors now have exactly 4 instances")
        
        return balanced_tubes

    @staticmethod
    def extract_json(text: str) -> Dict[str, Any]:
        """Extracts the first valid JSON object found within the text."""
        # Try to find JSON within potential markdown code blocks ```json ... ```
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Fallback: find the first '{' and last '}'
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            if start_idx != -1 and end_idx != 0:
                json_str = text[start_idx:end_idx]
            else:
                 # If no JSON structure is found, return the raw text for debugging
                return {"raw_response": text, "error": "No JSON object found in response"}

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
             # Return raw text and error if JSON parsing fails
            return {"raw_response": text, "error": f"Failed to parse JSON: {e}"}
        except Exception as e: # Catch other potential errors
            return {"raw_response": text, "error": f"An unexpected error occurred during JSON extraction: {e}"}
