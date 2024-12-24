{
  description = "Nix configuration for macOS with Homebrew integration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    nix-darwin.url = "github:LnL7/nix-darwin";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs@{ self, nix-darwin, nixpkgs, home-manager }: {
    darwinConfigurations = {
      hostname = nix-darwin.lib.darwinSystem {
        system = "aarch64-darwin";
        modules = [
          ./darwin-configuration.nix
          home-manager.nixosModules.home-manager
          {
            environment.systemPackages = [
            ];
            services.nix-daemon.enable = true;
            nix.settings.experimental-features = "nix-command flakes";
            security.pam.enableSudoTouchIdAuth = true;
            homebrew = {
              enable = true;
              taps = [
                "azure/kubelogin"
                "cloudflare/cloudflare"
                "homebrew/bundle"
                "idoavrah/homebrew"
                "jandedobbeleer/oh-my-posh"
                "julien-cpsn/atac"
                "mk-5/mk-5"
                "vladimirvivien/oss-tools"
              ];
              packages = [
                "azure/kubelogin/kubelogin"
                "cloudflare/cloudflare/cf-terraforming"
                "idoavrah/homebrew/tftui"
                "jandedobbeleer/oh-my-posh/oh-my-posh"
                "julien-cpsn/atac/atac"
                "mk-5/mk-5/fjira"
                "vladimirvivien/oss-tools/ktop"
              ];
              casks = [
                "alfred"
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
