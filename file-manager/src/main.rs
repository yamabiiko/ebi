use shelf::shelf::Shelf;
use std::path::PathBuf;

mod shelf;

fn main() {
    println!("Hello, world!");
    // Test
    Shelf::new(PathBuf::from("C:\\Users\\Alessandro\\Desktop\\Projects\\Tag-Based File Manager\\Automated Test Procedures\\Tests\\Workspaces\\Generated\\Directory"));
}
