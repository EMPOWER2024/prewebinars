import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# Initialize S3 Client (no region required)
s3_client = boto3.client('s3')

# Initialize the rich console for display
console = Console()

def display_welcome_message():
    """Display a welcome message using rich."""
    welcome_panel = Panel.fit(
        "[bold magenta]Welcome to EMPWR24 - Datathon![/bold magenta]\n"
        "[green]Let's get started with downloading some data![/green]\n\n"
        "[bold yellow]Graciously funded by:[/bold yellow]\n"
        "[cyan]AWS (Amazon)[/cyan], [cyan]CIC UC-Davis[/cyan]",
        title="🎉 [bold yellow]EMPWR24 Datathon[/bold yellow] 🎉",
        border_style="blue",
    )
    console.print(welcome_panel)

def choose_bucket_prefix():
    """Allow the user to choose a valid folder (prefix) from the main bucket."""
    prefixes = ['EMPWR-DS-QuadraHC', 'EMPWR-DS-QuantScient', 'EMPWR-DS-DONAN']
    console.print("\n[bold green]Please choose a data bucket (subdirectory) from the following options:[/bold green]")
    for idx, prefix in enumerate(prefixes, start=1):
        console.print(f"[bold cyan]{idx}.[/bold cyan] {prefix}")

    while True:
        choice = console.input("\n[bold yellow]Enter the number of the bucket you want to use (1-3): [/bold yellow] ")
        if choice in ['1', '2', '3']:
            return prefixes[int(choice) - 1]
        else:
            console.print("[red]Invalid choice. Please select a valid bucket number.[/red]")

def list_first_level_contents(bucket_name, prefix):
    """List the first-level subfolders and files inside the chosen prefix."""
    contents = []
    try:
        # List only the first-level subfolders and files in the prefix
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
        
        # Display subfolders (CommonPrefixes) with their sizes
        if 'CommonPrefixes' in response:
            console.print(f"\n[bold cyan]Subfolders in {prefix}:[/bold cyan]")
            for folder in response['CommonPrefixes']:
                folder_name = folder['Prefix']
                folder_size = calculate_subdirectory_size(bucket_name, folder_name)
                size_gb = folder_size / (1024 ** 3)  # Convert size to GB
                console.print(f"[cyan]📁 {folder_name} ({size_gb:.2f} GB)[/cyan]")
                contents.append(folder_name)
        
        # Display files at the root of the prefix
        if 'Contents' in response:
            console.print(f"\n[bold cyan]Files in {prefix}:[/bold cyan]")
            for obj in response['Contents']:
                if obj['Key'] == prefix:  # Skip the root itself
                    continue
                file_name = obj['Key']
                size_mb = obj['Size'] / (1024 ** 2)  # Convert size to MB
                console.print(f"[green]📄 {file_name} ({size_mb:.2f} MB)[/green]")
                contents.append(file_name)
        
        if not contents:
            console.print(f"[red]No files or subfolders found in {prefix}[/red]")
        
    except NoCredentialsError:
        console.print("[red]Credentials not available.[/red]")
    except ClientError as e:
        console.print(f"[red]Client error: {e}[/red]")
    
    return contents

def calculate_subdirectory_size(bucket_name, prefix):
    """Calculate the total size of all files within a subdirectory."""
    total_size = 0
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                total_size += obj['Size']  # Sum up the file sizes in bytes
    except ClientError as e:
        console.print(f"[red]Failed to calculate size for {prefix}: {e}[/red]")
    return total_size

def count_files_in_subfolder(bucket_name, folder_prefix):
    """Count the total number of files inside a subfolder."""
    total_files = 0
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' in response:
            total_files = len(response['Contents'])
    except ClientError as e:
        console.print(f"[red]Error counting files in subfolder {folder_prefix}: {e}[/red]")
    return total_files

def download_selected_items(bucket_name, selected_items, prefix, local_folder):
    """Download selected files or subfolders from S3."""
    total_files = 0

    # Pre-calculate total number of files (counting all files inside subfolders)
    for item in selected_items:
        if item['Key'].endswith('/'):
            total_files += count_files_in_subfolder(bucket_name, item['Key'])
        else:
            total_files += 1

    # Create the progress bar with a spinner and download progress
    with Progress(
        SpinnerColumn(spinner_name="dots", style="bold magenta"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        TextColumn("[bold cyan]{task.completed}/{task.total} files"),
        console=console,
    ) as progress:
        
        task = progress.add_task("[green]Downloading selected files...[/green]", total=total_files)
        
        for item in selected_items:
            key = item['Key']
            
            # Handle subfolder download: Download all files in the subfolder (prefix)
            if key.endswith('/'):
                download_subfolder(bucket_name, key, local_folder, progress, task)
            else:
                local_file_path = os.path.join(local_folder, key[len(prefix):].lstrip('/'))
                local_dir = os.path.dirname(local_file_path)

                # Create local directories if they don't exist
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)

                # Download the file
                s3_client.download_file(bucket_name, key, local_file_path)

                # Update progress
                progress.update(task, advance=1)
                console.print(f"[cyan]📥 Downloaded: {key} to {local_file_path}")

def download_subfolder(bucket_name, folder_prefix, local_folder, progress, task):
    """Download all files within a subfolder."""
    try:
        # List all files in the subfolder (prefix)
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                local_file_path = os.path.join(local_folder, key[len(folder_prefix):].lstrip('/'))
                local_dir = os.path.dirname(local_file_path)

                # Create local directories if they don't exist
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)

                # Download each file
                s3_client.download_file(bucket_name, key, local_file_path)

                # Update progress
                progress.update(task, advance=1)
                console.print(f"[cyan]📥 Downloaded: {key} to {local_file_path}")
    except ClientError as e:
        console.print(f"[red]Error downloading subfolder {folder_prefix}: {e}[/red]")

def browse_and_select_items(bucket_name, prefix):
    """Allow users to browse inside subdirectories and select files or subfolders to download."""
    selected_items = []
    
    while True:
        # List current directory contents
        contents = list_first_level_contents(bucket_name, prefix)
        if not contents:
            break
        
        # Ask user to select items to download or navigate into a subfolder
        selected = Prompt.ask(f"\n[bold yellow]Enter the name of the file/subfolder to download or type 'done' to finish, or enter a folder to browse:[/bold yellow]")
        
        if selected == 'done':
            break
        
        # Check if it's a valid selection
        if selected in contents:
            if selected.endswith('/'):  # If it's a subfolder
                action = Prompt.ask(f"[blue]Do you want to 'browse' into {selected} or 'download' it?[/blue]", choices=['browse', 'download'])
                if action == 'browse':
                    prefix = selected  # Update prefix and browse inside it
                elif action == 'download':
                    selected_items.append({'Key': selected})  # Add entire subfolder to the download list
            else:  # If it's a file, add it to the download list
                selected_items.append({'Key': selected})
        else:
            console.print(f"[red]Invalid selection: {selected}. Please choose a valid item from the list.[/red]")
    
    return selected_items

if __name__ == '__main__':
    # Display the welcome message
    display_welcome_message()

    # The actual S3 bucket name
    bucket_name = 'empower-datathon-prod-empowerdata-bcucxkzr'

    # Choose a folder (subdirectory) inside the bucket
    chosen_prefix = choose_bucket_prefix()

    # Ensure the prefix ends with '/' for proper folder listing
    if not chosen_prefix.endswith('/'):
        chosen_prefix += '/'

    # Browse the chosen directory and select items to download
    console.print(f"\n[bold cyan]Browsing {chosen_prefix}...[/bold cyan]")
    selected_items = browse_and_select_items(bucket_name, chosen_prefix)

    if selected_items:
        # Ask user where to save the downloaded items
        download_path = console.input("[blue]Enter the local folder path to save the items (e.g., /path/to/save/folder): [/blue]")
        
        # Download selected items
        download_selected_items(bucket_name, selected_items, chosen_prefix, download_path)
    else:
        console.print("[red]No items were selected for download.[/red]")

