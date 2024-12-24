{
  description = "Nix configuration for macOS with Homebrew integration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";  # Nixpkgs repository
    nix-darwin.url = "github:LnL7/nix-darwin";  # Nix-darwin repository for macOS
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";  # Ensure nix-darwin uses the same nixpkgs
    home-manager = {
      url = "github:nix-community/home-manager";  # Home Manager repository
      inputs.nixpkgs.follows = "nixpkgs";  # Ensure Home Manager uses the same nixpkgs
    };
  };

  outputs = inputs@{ self, nix-darwin, nixpkgs, home-manager }: {
    darwinConfigurations = {
      hostname = nix-darwin.lib.darwinSystem {
        system = "aarch64-darwin";  # Specify the system architecture for Apple Silicon Macs
        modules = [
          ./darwin-configuration.nix  # Include the main darwin configuration file
          home-manager.nixosModules.home-manager  # Include Home Manager module
          {
            environment.systemPackages = [
              # List of system-wide packages to be installed
            ];
            services.nix-daemon.enable = true;  # Enable the Nix daemon for multi-user support
            nix.settings.experimental-features = "nix-command flakes";  # Enable experimental Nix features
            security.pam.enableSudoTouchIdAuth = true;  # Enable Touch ID for sudo authentication
            homebrew = {
              enable = true;  # Enable Homebrew integration
              taps = [
                "azure/kubelogin"  # Additional Homebrew taps
                "cloudflare/cloudflare"
                "homebrew/bundle"
                "idoavrah/homebrew"
                "jandedobbeleer/oh-my-posh"
                "julien-cpsn/atac"
                "mk-5/mk-5"
                "vladimirvivien/oss-tools"
              ];
              packages = [
                "azure/kubelogin/kubelogin"  # Homebrew packages to be installed
                "cloudflare/cloudflare/cf-terraforming"
                "idoavrah/homebrew/tftui"
                "jandedobbeleer/oh-my-posh/oh-my-posh"
                "julien-cpsn/atac/atac"
                "mk-5/mk-5/fjira"
                "vladimirvivien/oss-tools/ktop"
              ];
              casks = [
                "alfred"  # Homebrew casks to be installed
                "docker"
                "iterm2"
                "signal"
                "slack"
                "spotify"
              ];
            };
          }
        ];
      };
    };
  };
}
