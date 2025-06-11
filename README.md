# MEGAcmd GUI

This project provides a simple web-based user interface for a recent build of [MEGAcmd](https://github.com/meganz/MEGAcmd), specifically compiled for Alpine on [GitHub](https://github.com/heidrich76/megacmd-alpine). It allows using MEGAcmd for synchronizing your files with the [MEGA cloud](https://mega.nz/).

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield]

> ⚠️ **Work in progress**: This add-on is provided _as-is_. Use at your own risk.


## Features

- **Logging In:** Authenticate and gain access to your MEGA account within the web interface.
- **File and Folder Synchronization:** Manage active synchronization tasks between local directories and your MEGA cloud storage.
- **WebDAV Access:** Potentially expose your MEGA cloud storage via WebDAV for integration with other applications or file managers.
- **Backup Management:** Dedicated functionality for creating and managing backups to your MEGA cloud storage.
- **Cloud Drive Mounting:** Mount your MEGA cloud storage as a local filesystem for seamless access through your operating system's file explorer.
- **Integrated Terminal Access:** Provides direct command-line access to MegaCMD for advanced operations and scripting within the web interface.
- [Complete MEGAcmd user guide](https://github.com/meganz/MEGAcmd/blob/master/UserGuide.md)


## Usage

To get the application up and running, you'll first download and start its Docker container.

- **Download and Start Container:** This command pulls the latest image from Docker Hub and forwards port `8080` to your host machine. For persistently storing configuration and synchronization data, a Docker volume named `root-volume` is created.
  ```bash
  docker run -d --name megacmd-gui -p 8080:8080 -v root-volume:/root jensheidrich76/megacmd-gui:latest
  ```
- **Start Shell in Container:** If you need to interact directly with the running container, this command opens an interactive bash shell:
  ```bash
  docker exec -it megacmd-gui /bin/bash
  ```

### FUSE-based Mounting of Cloud Folders (Experimental)

MegaCMD offers the capability to mount cloud folders to local directories using FUSE (Filesystem in Userspace). This feature is currently experimental, and thus requires special permissions for the container to function correctly.

To make the folder mounted within the container accessible outside on your host system, you must specify a bind propagation to a host-accessible directory. In the example provided below, we assume you have a designated folder `/mnt/mega` on your host. If you then mount any cloud folder to `/mnt/mega` *inside the container*, those files will become directly accessible on your host as well.

For Windows users, this functionality is primarily confined to the Docker-Desktop WSL environment, but the files can still be conveniently accessed via the Windows Explorer under the `Linux` file section at `\\wsl.localhost\docker-desktop\mnt\mega`.

* **Prepare Mounting Point (Windows-only):**
    For Windows users, it's necessary to prepare the mount point within the `docker-desktop` WSL2 environment.
    ```bash
    wsl -d docker-desktop # Switches to the Docker-Desktop WSL environment
    mkdir -p /mnt/mega  # Creates the directory to serve as the mount point
    exit                # Exits the WSL environment
    ```

* **Start Container with Bind Propagation:**
    This command initiates the container with the necessary FUSE permissions and sets up the recursive bind propagation from the prepared host folder to a folder within the container.
    ```bash
    docker run -d --name megacmd-gui -p 8080:8080 -v root-volume:/root --cap-add=SYS_ADMIN --device=/dev/fuse --security-opt apparmor:unconfined --mount type=bind,src=/mnt/mega,dst=/mnt/mega,bind-propagation=rshared jensheidrich76/megacmd-gui:latest
    ```
    This command grants the container the required permissions (`--cap-add=SYS_ADMIN`, `--device=/dev/fuse`, `--security-opt apparmor:unconfined`) for FUSE operations. It then establishes a recursive bind mount from the pre-created host directory `/mnt/mega` to `/mnt/mega` inside the container, ensuring that the FUSE mount performed within the container is properly propagated and visible on the host.


## Development Setup

Getting started with development is streamlined using VSCode Dev Containers. Follow these steps:

1.  **Clone the Repository and Open in VSCode:** Begin by cloning the project repository to your local machine. Once cloned, open the repository folder in VSCode. VSCode should automatically detect the dev container configuration.
2.  **Build and Start the Dev Container:** When prompted by VSCode, select "Reopen in Container" (or a similar option) to build and start the development container. This will set up your isolated development environment with all necessary dependencies.


## Building and Testing the Application

- For a quick build and to run the application's services in detached mode:
  ```bash
  docker-compose up --build -d
  ```
- To access a shell within your running development container (e.g., for debugging or running commands manually):
  ```bash
  docker exec -it megacmd-gui-dev /bin/bash
  ```
- Initiating a GitHub build by creating and pushing a tag to the repository:
  ```bash
  git tag -a v0.1.4 -m "Release v0.1.4"
  git push origin v0.1.4
  ```


[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
