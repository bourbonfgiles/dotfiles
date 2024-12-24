{
  description = "Nix configuration for macOS with Homebrew integration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    nix-darwin.url = "github:lnl7/nix-darwin";
    home-manager.url = "github:nix-community/home-manager";
  };

  outputs = { self, nixpkgs, nix-darwin, home-manager }: {
    darwinConfigurations = {
      hostname = nix-darwin.lib.darwinSystem {
        system = "x86_64-darwin";
        modules = [
          ./darwin-configuration.nix
          home-manager.nixosModules.home-manager
          {
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
